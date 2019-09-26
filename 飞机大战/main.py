import random

import pygame, sys, traceback
import my_plane
import enemy
import bullet
import supply

pygame.init()
pygame.mixer.init()

bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption("飞机大战")
background = pygame.image.load("./images/background.png").convert()

BLACK = (0, 0, 0)
RED = (0, 255, 0)
GREEN = (255, 0, 0)
WHITE = (255, 255, 255)

# 背景音乐载入
bg_music = pygame.mixer.music.load("./music/bg_music.mp3")
bg_music.set_volume(0,2)



def add_small_enemies(group1, group2, num):
    for i in range(num):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)


def add_mid_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)


def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.BIGEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)


def inc_speed(target, inc):
    for each in target:
        each.speed += inc


def main():
    running = True

    me = my_plane.MyPlane(bg_size)

    # 敌机汇众
    enemies = pygame.sprite.Group()

    # 生成敌方大型单位
    big_enemies = pygame.sprite.Group()
    add_big_enemies(big_enemies, enemies, 2)

    # 生成敌方中型单位
    mid_enemies = pygame.sprite.Group()
    add_mid_enemies(mid_enemies, enemies, 5)

    # 生成敌方小型单位
    small_enemies = pygame.sprite.Group()
    add_small_enemies(small_enemies, enemies, 15)

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BUTTEL_NUM = 4
    for i in range(BUTTEL_NUM):
        bullet1.append(bullet.Bullet1(me.rect.midtop))
    clock = pygame.time.Clock()

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BUTTEL2_NUM = 8
    for i in range(BUTTEL2_NUM // 2):
        bullet2.append(bullet.Bullet2((me.rect.centerx - 33, me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx + 33, me.rect.centery)))
    # 统计得分
    score = 0
    score_font = pygame.font.Font("C://Windows//Fonts//msyh.ttc", 36)

    # 暂停标记
    paused = False
    paused_nor_image = pygame.image.load("./images/pause_nor.png").convert_alpha()
    paused_pressed_image = pygame.image.load("./images/pause_pressed.png").convert_alpha()
    resume_nor_image = pygame.image.load("./images/resume_nor.png").convert_alpha()
    resume_pressed_image = pygame.image.load("./images/resume_pressed.png").convert_alpha()
    paused_rect = paused_nor_image.get_rect()
    paused_rect.left, paused_rect.top = width - paused_rect.width - 10, 10
    paused_image = paused_nor_image

    # 难度级别
    level = 1

    # 全屏炸弹
    bomb_image = pygame.image.load("./images/bomb.png").convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font("C://Windows//Fonts//msyh.ttc", 48)
    bomb_num = 3

    # 每30s触发补给
    bullet_supply = supply.Bullet_Suppy(bg_size)
    bomb_supply = supply.Bomb_Suppy(bg_size)
    SUPPLY_TIME = pygame.USEREVENT
    pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)

    # 中弹图像索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    me_destroy_index = 0

    # 结束界面
    gameover_font = pygame.font.Font("C://Windows//Fonts//msyh.ttc", 48)
    again_image = pygame.image.load("./images/again.png").convert_alpha()
    again_rect = again_image.get_rect()
    gameover_image = pygame.image.load("./images/gameover.png").convert_alpha()
    gameover_rect = gameover_image.get_rect()

    # 切换飞机图片
    switch_image = True

    # 超级子弹计时器
    DOUBLE_BULLET_TIME = pygame.USEREVENT + 1

    # 生命数量
    life_image = pygame.image.load("./images/life.png")
    life_rect = life_image.get_rect()
    life_num = 3

    # 标记是否使用超级子弹
    is_double_bullet = False

    # 无敌状态计时器
    INVINCIBLE_TIME = pygame.USEREVENT + 2

    # 用于阻止重复打开记录
    recorded = False

    # 用于延迟切换
    delay = 100

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and paused_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                    else:
                        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)


            elif event.type == pygame.MOUSEMOTION:
                if paused_rect.collidepoint(event.pos):
                    if paused:
                        paused_image = resume_pressed_image
                    else:
                        paused_image = paused_pressed_image
                else:
                    if paused:
                        paused_image = resume_nor_image
                    else:
                        paused_image = paused_nor_image

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each.active = False

            elif event.type == SUPPLY_TIME:
                if random.choice([True, False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()

            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)

            elif event.type == INVINCIBLE_TIME:
                me.invincible = False
                pygame.time.set_timer(INVINCIBLE_TIME, 0)

        # 得分提升游戏难度
        if level == 1 and score > 5000:
            level = 2
            add_small_enemies(small_enemies, enemies, 3)
            add_mid_enemies(mid_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 1)
            # 提升地方飞行速度
            inc_speed(small_enemies, 1)
        elif level == 2 and score > 30000:
            level = 3
            add_small_enemies(small_enemies, enemies, 3)
            add_mid_enemies(mid_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 1)
            # 提升地方飞行速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 3 and score > 100000:
            level = 4
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 2)
            add_big_enemies(big_enemies, enemies, 1)
            # 提升地方飞行速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
        elif level == 4 and score > 300000:
            level = 5
            add_small_enemies(small_enemies, enemies, 5)
            add_mid_enemies(mid_enemies, enemies, 3)
            add_big_enemies(big_enemies, enemies, 2)
            # 提升地方飞行速度
            inc_speed(small_enemies, 1)
            inc_speed(mid_enemies, 1)
            inc_speed(big_enemies, 1)

        screen.blit(background, (0, 0))

        if life_num and not paused:
            # 检测键盘操作
            key_pressed = pygame.key.get_pressed()
            if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
                me.moveUp()
            if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
                me.moveDown()
            if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
                me.moveLeft()
            if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
                me.moveRight()

            # 绘制炸弹补给 检测获得情况
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, me):
                    if bomb_num < 3:
                        bomb_num += 1
                    bomb_supply.active = False

            # 绘制子弹补给 检测获得情况
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me):
                    # 发射超级子弹
                    is_double_bullet = True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 18 * 1000)
                    bullet_supply.active = False

            # 发射子弹
            if not (delay % 10):
                if is_double_bullet:
                    bullets = bullet2
                    bullets[bullet2_index].reset((me.rect.centerx - 33, me.rect.centery))
                    bullets[bullet2_index + 1].reset((me.rect.centerx + 30, me.rect.centery))
                    bullet2_index = (bullet2_index + 2) % BUTTEL2_NUM
                else:
                    bullets = bullet1
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BUTTEL_NUM

            # 检测是否命中
            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemies_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemies_hit:
                        b.active = False
                        for e in enemies_hit:
                            if e in mid_enemies or e in big_enemies:
                                e.hit = True
                                e.energy -= 1
                                if e.energy <= 0:
                                    e.active = False
                            else:
                                e.active = False

            # 绘制大型敌机
            for each in big_enemies:
                if each.active:
                    each.move()
                    if each.hit:
                        # 被打特效
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        if switch_image:
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)

                        # 血槽
                        pygame.draw.line(screen, BLACK, (each.rect.left, each.rect.top - 5),
                                         (each.rect.right, each.rect.top - 5), 2)
                        # 当生命值大于20%显示绿色 否则显示红色
                        energy_remain = each.energy / enemy.BIGEnemy.energy
                        if energy_remain < 0.2:
                            energy_color = GREEN
                        else:
                            energy_color = RED
                        pygame.draw.line(screen, energy_color, (each.rect.left, each.rect.top - 5),
                                         (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5), 2)

                else:
                    # 毁灭
                    if not (delay % 3):
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e3_destroy_index = (e3_destroy_index + 1) % 6
                        if e3_destroy_index == 0:
                            score += 5000000
                            each.reset()

            # 绘制中型敌机
            for each in mid_enemies:
                if each.active:
                    each.move()
                    if each.hit:
                        # 被打特效
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)
                else:
                    if not (delay % 3):
                        screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 1500
                            each.reset()

                # 血槽
                pygame.draw.line(screen, BLACK, (each.rect.left, each.rect.top - 5),
                                 (each.rect.right, each.rect.top - 5), 2)
                # 当生命值大于20%显示绿色 否则显示红色
                energy_remain = each.energy / enemy.MidEnemy.energy
                if energy_remain < 0.2:
                    energy_color = GREEN
                else:
                    energy_color = RED
                pygame.draw.line(screen, energy_color, (each.rect.left, each.rect.top - 5),
                                 (each.rect.left + each.rect.width * energy_remain, each.rect.top - 5), 2)

            # 绘制小型敌机
            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    if not (delay % 3):
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index + 1) % 4
                        if e1_destroy_index == 0:
                            score += 500
                            each.reset()

            # 检测碰撞
            enemies_down = pygame.sprite.spritecollide(me, enemies, False, pygame.sprite.collide_mask)
            if enemies_down and not me.invincible:
                me.active = False
                for e in enemies_down:
                    e.active = False

            # 绘制我方飞机
            if me.active:
                if delay % 5:
                    switch_image = not switch_image
                if switch_image:
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:
                if not (delay % 3):
                    screen.blit(me.destroy_images[me_destroy_index], me.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        life_num -= 1
                        me.reset()
                        bomb_num = 3
                        pygame.time.set_timer(INVINCIBLE_TIME, 3 * 1000)

            # 绘制剩余炸弹
            bomb_text = bomb_font.render("X %d" % bomb_num, True, WHITE)
            text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(bomb_text, (20 + bomb_rect.width, height - 5 - text_rect.height))

            # 绘制生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image, (width - 10 - (i + 1) * life_rect.width, height - 10 - life_rect.height))

            # 绘制游戏结束画面
            elif life_num == 0:
                print("Game over")

            # 绘制得分
            score_text = score_font.render("Score : %s" % str(score), True, WHITE)
            screen.blit(score_text, (10, 5))

        # 游戏结束画面
        elif life_num == 0:
            pygame.time.set_timer(SUPPLY_TIME, 0)

            if not recorded:
                recorded = True
                # 读取最高分
                with open("./record.txt", "r") as f:
                    record_score = int(f.read())
                    # 判断分数高低
                    if score > record_score:
                        with open("./record.txt", "w") as f:
                            f.write(str(score))
                        record_score = score

            # 绘制界面
            record_score_text = score_font.render("Best : %s" % record_score, True, WHITE)
            screen.blit(record_score_text, (30, 30))

            gameover_text1 = gameover_font.render("Your Score", True, WHITE)
            gameover_text1_rect = gameover_text1.get_rect()
            gameover_text1_rect.left, gameover_text1_rect.top = (width - gameover_text1_rect.width) // 2, height - 550
            screen.blit(gameover_text1, gameover_text1_rect)

            gameover_text2 = gameover_font.render(str(score), True, WHITE)
            gameover_text2_rect = gameover_text2.get_rect()
            gameover_text2_rect.left, gameover_text2_rect.top = (width - gameover_text2_rect.width) // 2, gameover_text1_rect.bottom + 50
            screen.blit(gameover_text2, gameover_text2_rect)

            again_rect.left, again_rect.top = (width - again_rect.width) // 2, gameover_text2_rect.bottom + 50
            screen.blit(again_image, again_rect)
            gameover_rect.left, gameover_rect.top = (width - again_rect.width) // 2, again_rect.bottom + 30
            screen.blit(gameover_image, gameover_rect)

            # 检测用户鼠标动作
            if pygame.mouse.get_pressed()[0]:
                # 获取鼠标位置
                pos = pygame.mouse.get_pos()
                if again_rect.left < pos[0] < again_rect.right and again_rect.top < pos[1] < again_rect.bottom:
                    # 重新开始
                    main()
                elif gameover_rect.left < pos[0] < gameover_rect.right and gameover_rect.top < pos[
                    1] < gameover_rect.bottom:
                    # 退出
                    pygame.quit()
                    sys.exit()



        # 绘制暂停按钮
        screen.blit(paused_image, paused_rect)

        delay -= 1
        if not delay:
            delay = 100

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
