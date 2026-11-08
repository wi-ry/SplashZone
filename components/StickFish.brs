sub init()
    m.spine = m.top.findNode("Spine")
    m.upperLeft = m.top.findNode("UpperLeft")
    m.upperRight = m.top.findNode("UpperRight")
    m.lowerLeft = m.top.findNode("LowerLeft")
    m.lowerRight = m.top.findNode("LowerRight")
    m.tailUpper = m.top.findNode("TailUpper")
    m.tailLower = m.top.findNode("TailLower")
    m.eye = m.top.findNode("Eye")

    m.top.observeField("fishColor", "onFishColorChanged")
    onFishColorChanged()
end sub

sub onFishColorChanged() as void
    color = m.top.fishColor
    m.spine.color = color
    m.upperLeft.color = color
    m.upperRight.color = color
    m.lowerLeft.color = color
    m.lowerRight.color = color
    m.tailUpper.color = color
    m.tailLower.color = color
    m.eye.color = color
end sub
