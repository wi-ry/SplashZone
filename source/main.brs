sub RunScreenSaver()
    screen = CreateObject("roSGScreen")
    port = CreateObject("roMessagePort")
    screen.SetMessagePort(port)

    screen.CreateScene("AquariumScene")
    screen.Show()

    while true
        message = Wait(0, port)
        if message <> invalid
            if type(message) = "roSGScreenEvent"
                if message.IsScreenClosed()
                    return
                end if
            end if
        end if
    end while
end sub
