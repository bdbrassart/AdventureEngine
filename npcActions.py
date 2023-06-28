def npcID_1(npcObj, window, event, stopEvent):
    # Reginald Kensington
    while not stopEvent.is_set():
        window.addstr("test npc 1\n\n")
        event.wait(5)
        window.refresh()

def npcID_2(npcObj, window, event, stopEvent):
    while not stopEvent.is_set():
        window.addstr("test npc 2\n\n")
        event.wait(3)
        window.refresh()