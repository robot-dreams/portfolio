R = 40
GAP = R / 6.0
BORDER_RADIUS = 20
CHILD_LINE_Y1 = 3.5 * R
CHILD_LINE_Y2 = 1.5 * R
SPOUSE_GAP_X = R / 2
SPOUSE_CENTER_DX = 2 * R + SPOUSE_GAP_X
CHILD_GAP_X = R
NAME_OFFSET = 1.5 * R

LIGHT_GRAY = '#e7eaf6'
BLUE = '#38598b'
DARK_BLUE = '#113f67'

"""
TODO:
- Calculate height / automatically center vertically
- Fix issue with children of later spouses

UI improvement ideas:
- Increase vertical spacing for balance?
- Should moms always be on the left?
- Slightly more padding between cousins than siblings?
- Add more info (e.g. gender, birthdays, deceased or not)?
"""

class Node:
    def __init__(self, name, spouse=None, lsqueeze=False, rsqueeze=False, duplicate=False):
        self.name = name
        self.spouse = spouse
        self.lsqueeze = lsqueeze
        self.rsqueeze = rsqueeze
        self.duplicate = duplicate

    def extent(self, child_only=False):
        if self.spouse is None:
            return R, R
        else:
            children = self.spouse.children
            if len(children) == 0:
                if self.duplicate:
                    return R, R
                else:
                    return R, self.spouse_dx() + R
            else:
                wsum = (len(children) - 1) * CHILD_GAP_X
                for child in children:
                    wsum += sum(child.extent())
                lc = (wsum - self.spouse_dx()) / 2
                rc = (wsum + self.spouse_dx()) / 2
                if child_only:
                    return lc, rc
                if self.lsqueeze:
                    lc = min(R, lc)
                else:
                    lc = max(R, lc)
                if self.rsqueeze:
                    rc = min(self.spouse_dx() + R, rc)
                else:
                    rc = max(self.spouse_dx() + R, rc)
                return lc, rc

    def spouse_dx(self):
        if self.duplicate:
            return 0
        else:
            return SPOUSE_CENTER_DX

    # Precondition: origin is where top center of node should be placed
    def render(self):
        if not self.duplicate:
            node(0, R, self.name)
        l, r = self.extent()
        if self.spouse is None:
            return
        spouse = self.spouse
        node(self.spouse_dx(), R, spouse.name)
        children = spouse.children
        child_line = len(children) > 0
        if not self.duplicate:
            connect(0, R, self.spouse_dx(), R, child_line=child_line)
        if len(children) == 1:
            line(self.spouse_dx() / 2, CHILD_LINE_Y1, self.spouse_dx() / 2, CHILD_LINE_Y1 + CHILD_LINE_Y2)
            pushMatrix()
            translate(self.spouse_dx() / 2, CHILD_LINE_Y1 + CHILD_LINE_Y2)
            children[0].render()
            popMatrix()
        elif len(children) > 1:
            l, r = self.extent(child_only=True)
            l_oldest, _ = children[0].extent()
            _, r_youngest = children[-1].extent()
            line(-l + l_oldest + BORDER_RADIUS, CHILD_LINE_Y1, r - r_youngest - BORDER_RADIUS, CHILD_LINE_Y1)
            pushMatrix()
            translate(-l, CHILD_LINE_Y1 + CHILD_LINE_Y2)
            for i, child in enumerate(children):
                l_child, r_child = child.extent()
                if child.duplicate:
                    i0 = [c.name for c in children].index(child.name)
                    centers = [(l_child, R)]
                    for j in range(i - 1, i0 - 1, -1):
                        x, y = centers[-1]
                        x -= children[j + 1].extent()[0]
                        x -= CHILD_GAP_X
                        x -= children[j].extent()[1] - SPOUSE_CENTER_DX
                        centers.append((x, y))
                        if j == i0:
                            centers.append((x - SPOUSE_CENTER_DX, y))
                    n = len(centers)
                    for k in range(n - 1):
                        x1, y1 = centers[k + 1]
                        x2, y2 = centers[k]
                        h = k * GAP
                        rdst = R + h
                        rsrc = R if k == n - 2 else rdst + GAP
                        if k < n - 2:
                            partial_arc(x1, y1, rsrc, h + GAP, h)
                        child_line = k == 0 and len(child.spouse.children) > 0
                        connect(x1, y1, x2, y2, rsrc, rdst, h, child_line=child_line)
                
                translate(l_child, 0)
                if i == 0:
                    line(0, -CHILD_LINE_Y2 + BORDER_RADIUS, 0, 0)
                    noFill()
                    arc(BORDER_RADIUS, -CHILD_LINE_Y2 + BORDER_RADIUS, 2 * BORDER_RADIUS, 2 * BORDER_RADIUS, -PI, -HALF_PI)
                elif i == len(children) - 1:
                    line(0, -CHILD_LINE_Y2 + BORDER_RADIUS, 0, 0)
                    noFill()
                    arc(-BORDER_RADIUS, -CHILD_LINE_Y2 + BORDER_RADIUS, 2 * BORDER_RADIUS, 2 * BORDER_RADIUS, -HALF_PI, 0)
                elif not child.duplicate:
                    line(0, -CHILD_LINE_Y2, 0, 0)
                child.render()
                translate(CHILD_GAP_X + r_child, 0)

            popMatrix()

class Spouse:
    def __init__(self, name, *children):
        self.name = name
        self.children = children

def node(x0, y0, name):
    img = loadImage(name.replace('\n', ' ') + '.png')
    if img is None:
        img = placeholder
    image(img, x0 - R, y0 - R, 2 * R, 2 * R)
    noFill()
    circle(x0, y0, 2 * R)
    fill(DARK_BLUE)
    text(name, x0, y0 + NAME_OFFSET)

def connect(xsrc, ysrc, xdst, ydst, rsrc=R, rdst=R, h=0, child_line=True):
    theta1 = asin(1.0 * h / rsrc)
    x1 = xsrc + rsrc * cos(theta1)
    y1 = ysrc - rsrc * sin(theta1)
    theta2 = asin(1.0 * h / rdst)
    x2 = xdst - rdst * cos(theta2)
    y2 = ydst - rdst * sin(theta2)
    line(x1, y1, x2, y2)
    if child_line:
        x = x2 - SPOUSE_GAP_X / 2
        line(x, y2, x, y2 + CHILD_LINE_Y1 - R)

def partial_arc(x, y, r, h1, h2):
    theta1 = asin(1.0 * h1 / r)
    theta2 = asin(1.0 * h2 / r)
    noFill()
    arc(x, y, 2 * r, 2 * r, -PI + theta1, -theta2, OPEN)

def setup():
    global placeholder

    # fullScreen()
    size(1600, 900)
    pixelDensity(2)
    background(LIGHT_GRAY)
    font = createFont('Nunito-SemiBold.ttf', 13.5, True)
    textFont(font)
    textAlign(CENTER)
    textLeading(16)
    strokeWeight(2)
    stroke(BLUE)
    noFill()
    noLoop()
    placeholder = loadImage('Placeholder.png')

tree = Node('Elizabeth II',
            Spouse('Philip',
                Node('Charles III',
                    Spouse('Diana\nSpencer',
                        Node('William',
                            Spouse('Catherine\nMiddleton',
                                Node('George'),
                                Node('Charlotte'),
                                Node('Louis'))),
                        Node('Harry',
                             Spouse('Meghan\nMarkle',
                                Node('Archie'),
                                Node('Lilibet')))), rsqueeze=True),
                Node('Charles III',
                    Spouse('Camilla\nShand'), duplicate=True),
                Node('Anne',
                    Spouse('Mark\nPhillips')),
                Node('Anne',
                    Spouse('Timothy\nLaurence'), duplicate=True),
                Node('Andrew',
                    Spouse('Sarah\nFerguson',
                        Node('Beatrice'),
                        Node('Eugenie'))),
                Node('Edward',
                    Spouse('Sophie\nRhys-Jones',
                        Node('Louise'),
                        Node('James')))))
    
def draw():
    translate((width - SPOUSE_CENTER_DX) / 2, (height - 3 * (CHILD_LINE_Y1 + CHILD_LINE_Y2) - 2 * R) / 2)
    tree.render()
    saveFrame('family-tree.png')
