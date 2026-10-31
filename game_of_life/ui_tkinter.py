from time import monotonic, sleep
from typing import Any, Callable
import tkinter as tk

import numpy as np

from .event_handling import Event, EventSubscriber, EventType
from .ui import UI, UIBuilder, UIBuilderError, UIColor, UIElement, UIWindow

UI_FRAME_RATE = 60


def _tk_color(color: UIColor) -> str:
    """Convert an RGB UI color to Tk's hexadecimal color notation."""
    red, green, blue = color.value
    return f'#{red:02x}{green:02x}{blue:02x}'


class TkinterUIWindow(UIWindow):
    """Own the Tk root window and drawing canvas."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.root: tk.Tk | None = None
        self.canvas: tk.Canvas | None = None

    def setup(self) -> None:
        self.root = tk.Tk()
        self.root.title("Conway's Game of Life")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            background=_tk_color(UIColor.WHITE),
            highlightthickness=0,
        )
        self.canvas.pack()

    def clear(self) -> None:
        pass

    def set_close_handler(self, handler: Callable[[], None]) -> None:
        self.get_root().protocol('WM_DELETE_WINDOW', handler)

    def get_root(self) -> tk.Tk:
        if self.root is None:
            raise RuntimeError("Tkinter window has not been set up")
        return self.root

    def get_canvas(self) -> tk.Canvas:
        if self.canvas is None:
            raise RuntimeError("Tkinter canvas has not been set up")
        return self.canvas

    def close(self) -> None:
        if self.root is None:
            return
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        finally:
            self.root = None
            self.canvas = None


class TkinterUIGrid(UIElement):
    """Render the simulation board on a Tk canvas."""

    def __init__(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        super().__init__()
        self.n_cells_x = n_cells_x
        self.n_cells_y = n_cells_y
        self.cell_width = cell_width
        self.cell_height = cell_height
        self._cells: list[int] = []
        self._values = np.full((n_cells_x, n_cells_y), -1, dtype=np.int8)

    def draw(self, window: UIWindow, **kwargs: Any) -> None:
        if not isinstance(window, TkinterUIWindow):
            raise TypeError("TkinterUIGrid requires a TkinterUIWindow")
        canvas = window.get_canvas()
        board_state = kwargs.get('board_state', np.zeros((self.n_cells_x, self.n_cells_y)))
        if not self._cells:
            self._create_cells(canvas)
        for (x, y), value in np.ndenumerate(board_state):
            normalized_value = int(bool(value))
            if self._values[x, y] == normalized_value:
                continue
            fill = UIColor.BLACK if normalized_value else UIColor.WHITE
            outline = UIColor.BLACK if normalized_value else UIColor.GRAY
            cell_index = x * self.n_cells_y + y
            canvas.itemconfigure(
                self._cells[cell_index],
                fill=_tk_color(fill),
                outline=_tk_color(outline),
            )
            self._values[x, y] = normalized_value

    def _create_cells(self, canvas: tk.Canvas) -> None:
        for x in range(self.n_cells_x):
            for y in range(self.n_cells_y):
                left = x * self.cell_width
                top = y * self.cell_height
                self._cells.append(canvas.create_rectangle(
                    left,
                    top,
                    left + self.cell_width,
                    top + self.cell_height,
                    fill=_tk_color(UIColor.WHITE),
                    outline=_tk_color(UIColor.GRAY),
                    tags='grid',
                ))


class TkinterUIButton(UIElement):
    """Publish a configured event from a native Tk button."""

    def __init__(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        super().__init__()
        self.label = label
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.event = event
        self.widget: tk.Button | None = None

    def mount(self, window: TkinterUIWindow) -> None:
        self.widget = tk.Button(window.get_root(), text=self.label, command=self.on_click)
        self.widget.place(x=self.x, y=self.y, width=self.width, height=self.height)

    def draw(self, window: UIWindow, **kwargs: Any) -> None:
        pass

    def on_click(self) -> None:
        self.publish(self.event)


class TkinterUISlider(UIElement):
    """Publish numeric changes from a native horizontal Tk scale."""

    def __init__(self, x: int, y: int, width: int, height: int,
                 min_value: float, max_value: float,
                 initial_value: float, event: EventType) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.event = event
        self.widget: tk.Scale | None = None
        self.variable: tk.DoubleVar | None = None

    def mount(self, window: TkinterUIWindow) -> None:
        self.variable = tk.DoubleVar(window.get_root(), value=self.value)
        self.widget = tk.Scale(
            window.get_root(),
            from_=self.min_value,
            to=self.max_value,
            orient=tk.HORIZONTAL,
            resolution=0.1,
            showvalue=True,
            variable=self.variable,
            command=self.on_change,
        )
        self.widget.place(x=self.x, y=self.y, width=self.width, height=self.height + 30)

    def draw(self, window: UIWindow, **kwargs: Any) -> None:
        pass

    def on_change(self, value: str) -> None:
        new_value = float(value)
        if new_value == self.value:
            return
        self.value = new_value
        self.publish(self.event, self.value)


class TkinterUI(UI, EventSubscriber):
    """Implement UI input, rendering, and frame pacing with Tkinter."""

    def __init__(self, screen: TkinterUIWindow, grid: TkinterUIGrid,
                 buttons: list[TkinterUIButton], sliders: list[TkinterUISlider] | None = None) -> None:
        super().__init__()
        self.screen = screen
        self.screen.setup()
        self.screen.set_close_handler(self._on_close)
        self.grid = grid
        self.buttons = buttons
        self.sliders = sliders or []
        self._frame_started_at = monotonic()
        for element in [*self.buttons, *self.sliders]:
            element.mount(self.screen)
            element.attach(self)

    def notify(self, event: Event) -> None:
        self.publish(event.event_type, event.payload)

    def render(self, board_state: np.ndarray) -> None:
        self.screen.clear()
        self.grid.draw(self.screen, board_state=board_state)

    def process_events(self) -> None:
        try:
            root = self.screen.get_root()
            root.update_idletasks()
            root.update()
        except tk.TclError:
            self.publish(EventType.UI_QUIT)

    def finish_frame(self) -> None:
        remaining = 1.0 / UI_FRAME_RATE - (monotonic() - self._frame_started_at)
        if remaining > 0:
            sleep(remaining)
        self._frame_started_at = monotonic()

    def close(self) -> None:
        self.screen.close()

    def _on_close(self) -> None:
        self.publish(EventType.UI_QUIT)


class TkinterUIBuilder(UIBuilder):
    """Build complete Tkinter UIs while enforcing component construction order."""

    def __init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self.screen: TkinterUIWindow | None = None
        self.grid: TkinterUIGrid | None = None
        self.buttons: list[TkinterUIButton] = []
        self.sliders: list[TkinterUISlider] = []

    def build_window(self, width: int, height: int) -> None:
        if self.screen is not None:
            raise UIBuilderError("window has already been built for the current UI")
        self.screen = TkinterUIWindow(width, height)

    def build_grid(self, n_cells_x: int, n_cells_y: int, cell_width: int, cell_height: int) -> None:
        self._require_window()
        if self.grid is not None:
            raise UIBuilderError("grid has already been built for the current UI")
        self.grid = TkinterUIGrid(n_cells_x, n_cells_y, cell_width, cell_height)

    def build_button(self, label: str, width: int, height: int, x: int, y: int, event: EventType) -> None:
        self._require_grid()
        self.buttons.append(TkinterUIButton(label, width, height, x, y, event))

    def build_slider(self, x: int, y: int, width: int, height: int, min_value: float,
                    max_value: float, initial_value: float, event: EventType) -> None:
        self._require_grid()
        self.sliders.append(TkinterUISlider(x, y, width, height, min_value, max_value, initial_value, event))

    def get_ui(self) -> TkinterUI:
        screen = self._require_window()
        grid = self._require_grid()
        ui = TkinterUI(screen, grid, self.buttons, self.sliders)
        self._reset()
        return ui

    def _require_window(self) -> TkinterUIWindow:
        if self.screen is None:
            raise UIBuilderError("build the window before other UI components")
        return self.screen

    def _require_grid(self) -> TkinterUIGrid:
        self._require_window()
        if self.grid is None:
            raise UIBuilderError("build the grid before controls or product retrieval")
        return self.grid