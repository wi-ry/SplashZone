sub init()
    m.top.backgroundColor = "0x06243FFF"
    m.top.backgroundUri = ""

    m.fishNodes = [
        m.top.findNode("FishOne"),
        m.top.findNode("FishTwo"),
        m.top.findNode("FishThree"),
        m.top.findNode("FishFour")
    ]
    m.fishSpeeds = [2.2, 3.0, 1.8, 3.6]
    m.bubbleNodes = [
        m.top.findNode("BubbleOne"),
        m.top.findNode("BubbleTwo"),
        m.top.findNode("BubbleThree"),
        m.top.findNode("BubbleFour")
    ]
    m.bubbleSpeeds = [2.4, 1.8, 2.8, 2.1]
    m.motionStarted = false

    m.motionTimer = m.top.findNode("MotionTimer")
    if m.motionTimer = invalid
        print "[Splash Zone] Missing MotionTimer node"
        return
    end if

    m.motionTimer.observeField("fire", "onMotionTick")
    m.motionTimer.control = "start"
    print "[Splash Zone] Motion timer started"
end sub

sub onMotionTick()
    if not m.motionStarted
        print "[Splash Zone] Motion timer tick received"
        m.motionStarted = true
    end if

    for index = 0 to m.fishNodes.count() - 1
        fish = m.fishNodes[index]
        if fish <> invalid
            position = fish.translation
            fishX = position[0] + m.fishSpeeds[index]
            if fishX > 1980
                fishX = -150
            end if
            fish.translation = [fishX, position[1]]
        end if
    end for

    for index = 0 to m.bubbleNodes.count() - 1
        bubble = m.bubbleNodes[index]
        if bubble <> invalid
            position = bubble.translation
            bubbleY = position[1] - m.bubbleSpeeds[index]
            if bubbleY < -40
                bubbleY = 1120
            end if
            bubble.translation = [position[0], bubbleY]
        end if
    end for
end sub
