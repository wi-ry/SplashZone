sub init()
    m.top.backgroundColor = "0x06243FFF"
    m.top.backgroundUri = ""

    m.top.findNode("FishOneSwim").control = "start"
    m.top.findNode("FishTwoSwim").control = "start"
    m.top.findNode("FishThreeSwim").control = "start"
    m.top.findNode("FishFourSwim").control = "start"
    m.top.findNode("BubbleOneRise").control = "start"
    m.top.findNode("BubbleTwoRise").control = "start"
    m.top.findNode("BubbleThreeRise").control = "start"
    m.top.findNode("BubbleFourRise").control = "start"
end sub
