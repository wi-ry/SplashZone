sub init()
    m.top.backgroundColor = "0x06243FFF"
    m.top.backgroundUri = ""

    startAnimation("FishOneSwim")
    startAnimation("FishTwoSwim")
    startAnimation("FishThreeSwim")
    startAnimation("FishFourSwim")
    startAnimation("BubbleOneRise")
    startAnimation("BubbleTwoRise")
    startAnimation("BubbleThreeRise")
    startAnimation("BubbleFourRise")
end sub

sub startAnimation(nodeId as string)
    animation = m.top.findNode(nodeId)
    if animation = invalid
        print "[Splash Zone] Missing animation node: "; nodeId
        return
    end if

    animation.control = "start"
end sub
