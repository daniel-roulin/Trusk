from renderer import Renderer
import math

TEXT = "Hello World! This is a common greeting often used as a first test for a new software or system. It is a simple and straightforward way to verify that the basic functionality is working as expected. It has become a standard in the software development industry and is widely recognized by developers and computer enthusiasts alike. The phrase \"Hello World!\" has become a symbol for starting a new journey in programming, and it is often the first step for many in learning how to code."
def main():
    r = Renderer(width=100, height=100, target_fps=30)
    time = 0
    while True:
        time += 1

        r.line(math.cos(time/10) * 15 + 100/6, math.sin(time/10) * 15 + 100/6, math.cos(math.pi + time/10) * 15 + 100/6, math.sin(math.pi + time/10) * 15 + 100/6)
        r.point(math.cos(time/10) * 15 + 100/6*3, math.sin(time/14) * 15 + 100/6)
        r.text(100/3*2 + 5, 100/6, TEXT[time % len(TEXT):(time + 12) % len(TEXT)])

        r.rect(math.cos(time/10) * 5 + 10, math.cos(time/13) * 5 + 10 + 100/3*2, abs(math.cos(time/11))*20, abs(math.cos(time/15))*20)
        r.filled_rect(math.cos(time/11) * 5 + 10, math.cos(time/12) * 5 + 10 + 100/3, abs(math.cos(time/9))*20, abs(math.cos(time/7))*20)
        
        r.ellipse(math.cos(time/12) * 5 + 50, math.cos(time/7) * 5 + 100/6*5, abs(math.cos(time/12))*20, abs(math.cos(time/14))*20)
        r.filled_ellipse(math.cos(time/8) * 5 + 50, math.cos(time/11) * 5 + 50, abs(math.cos(time/10))*20, abs(math.cos(time/12))*20)

        r.triangle(math.cos(time/10) * 15 + 100/6*5, math.sin(time/10) * 15 + 100/6*5, math.cos(time/10 + 2/3*math.pi) * 15 + 100/6*5, math.sin(time/10 + 2/3*math.pi) * 15 + 100/6*5, math.cos(time/10 + 4/3*math.pi) * 15 + 100/6*5, math.sin(time/10 + 4/3*math.pi) * 15 + 100/6*5)
        r.filled_triangle(math.cos(-time/10) * 15 + 100/6*5, math.sin(-time/10) * 15 + 50, math.cos(-time/10 + 2/3*math.pi) * 15 + 100/6*5, math.sin(-time/10 + 2/3*math.pi) * 15 + 50, math.cos(-time/10 + 4/3*math.pi) * 15 + 100/6*5, math.sin(-time/10 + 4/3*math.pi) * 15 + 50)
    
        r.draw()
        
if __name__ == "__main__":
    main()