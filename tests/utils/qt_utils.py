from PySide6.QtCore import QCoreApplication, QEvent

def close_qt_window(window, app=None) -> None:
    active_app = app or QCoreApplication.instance()
    if hasattr(window, "_is_closing"):
        window._is_closing = True
    if active_app is not None:
        active_app.processEvents()
        active_app.processEvents()
    view_controller = getattr(window, "view_controller", None)
    timer = getattr(view_controller, "_tree_rebuild_timer", None)
    if timer is not None:
        try:
            timer.stop()
        except RuntimeError:
            pass
    restore_worker = getattr(window, "_restore_session_worker", None)
    if restore_worker is not None:
        try:
            if restore_worker.isRunning():
                restore_worker.wait(1000)
        except (AttributeError, RuntimeError):
            pass
    window.close()
    window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
    if active_app is not None:
        active_app.processEvents()
        active_app.processEvents()