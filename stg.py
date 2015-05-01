# -*- coding:utf-8 -*-
##
# @file stg.py
# @brief
# @author Hayato Sasaki
# @version 1
# @date 2015-04-29
import pygame
import pygame.display
import pygame.sprite
import random
import collections


## ゲーム画面のサイズ
SIZE = (640, 480)


##
# @brief Rectが画面外に出ていないかを判定する関数
#
# @param rect 判定対象となるRectオブジェクト
#
# @return 0番目がx座標,1番目がy座標が範囲外かどうかをbool値で保持するtupple
def checkOutOfRange(rect):
    x = rect.center[0]
    y = rect.center[1]
    X = SIZE[0]
    Y = SIZE[1]
    width = rect.width
    height = rect.height

    isOutOfRange = [False, False]
    if not (0 + width / 2 < x < X - width / 2):
        isOutOfRange[0] = True
    if not (0 + height / 2 < y < Y - height / 2):
        isOutOfRange[1] = True

    return tuple(isOutOfRange)


##
# @brief 自作のSpriteクラス
#
# 自作のSpriteクラスでpygame.sprite.Spriteクラスを継承している.
class MySprite(pygame.sprite.Sprite):
    ##
    # @brief MySpriteクラスのコンストラクタ
    #
    # @param image  spriteに設定する画像
    # @param pos    spriteの初期座標
    # @param drawGroup  spriteの描画を管理するgroupオブジェクト
    def __init__(self, image, pos, drawGroup):
        # 親クラス(Spriteクラス)のコンストラクタ
        pygame.sprite.Sprite.__init__(self, drawGroup)
        ## このオブジェクトが属する描画グループ
        self.drawGroup = drawGroup
        ## spriteの画像
        self.image = image
        ## spriteの四角形領域
        self.rect = self.image.get_rect()
        # spriteの初期位置を設定
        self.rect.center = pos
        ## spriteの移動速度
        self._v = [0, 0]

    ##
    # @brief 画面内を移動するメソッド
    #
    # self._vに基づいて移動を行う.
    def _move(self):
        self.rect.move_ip(self._v[0], self._v[1])


##
# @brief 弾丸クラス
#
# 弾丸クラスで,MySpriteクラスを継承している.
class Bullet(MySprite):
    ##
    # @brief Bulletクラスのコンストラクタ
    #
    # @param pos 弾丸の初期位置
    # @param bprop 弾丸の属性(攻撃力や画像など)
    # @param drawGroup  spriteの描画を管理するgroupオブジェクト
    # @param bulletGroup 弾丸をまとめて管理するためのgroupオブジェクト
    def __init__(self, pos, bprop, drawGroup, bulletGroup):
        MySprite.__init__(self, bprop.image, pos, drawGroup)
        super(MySprite, self).add(bulletGroup)
        ## 弾丸の属性(攻撃力や画像などの静的なもの)
        self.prop = bprop
        ## 弾丸の速度
        self._v = self.prop.v

    ##
    # @brief 状態の更新メソッド
    #
    # self._vに基づいて移動を行い，弾丸の状態を更新する
    def update(self):
        self._move()
        isOutOfRangeTupple = checkOutOfRange(self.rect)
        isOutOfRange = isOutOfRangeTupple[0] or isOutOfRangeTupple[1]
        if isOutOfRange:
            self.kill()

    ##
    # @brief 衝突したオブジェクトに対してダメージを与えるメソッド
    #
    # @param airflame ダメージを与える対象となるオブジェクト
    #
    # 衝突したオブジェクトに対してダメージを与える.なお,衝突した後は弾丸自身は消滅する.
    def damage(self, airflame):
        airflame.collided(self.prop.d)
        self.kill()


##
# @brief 機体を表すクラス
#
# 機体を表すクラスでMySpriteを継承している.
class Airflame(MySprite):
    ##
    # @brief Airflameクラスのコンストラクタ
    #
    # @param pos 機体の初期値
    # @param prop 機体の属性(静的なもの)
    # @param drawGroup spriteの描画を管理するGroupオブジェクト
    # @param bulletGroup 弾丸をまとめて管理するためのGroupオブジェクト
    def __init__(self, pos, prop, drawGroup, bulletGroup):
        MySprite.__init__(self, prop.image, pos, drawGroup)
        ## 機体が生成するBulletオブジェクトの所属するグループ
        self.bulletGroup = bulletGroup
        ## 機体の属性(静的なもの)
        self.prop = prop
        ## 機体のヒットポイント
        self._hp = prop.hp
        ## 機体が弾丸を撃ってからの経過時間
        self._reload = prop.reloadLimit
        ## 機体が弾丸を撃とうとしているかどうかを表すbool値
        self._isShot = False

    ##
    # @brief 弾丸を発射するメソッド
    #
    # self._isShotおよびself._reloadの値が条件を満たしている場合に，弾丸を発射する.
    def _shot(self):
        if self._isShot:
            if self._reload > self.prop.reloadLimit:
                # 生成する弾丸の初期位置を設定
                bulletPos = self.rect.center
                # 生成する弾丸のプロパティを設定
                bulletProp = self.prop.bprop
                # 弾丸の生成
                Bullet(bulletPos, bulletProp, self.drawGroup, self.bulletGroup)
                # リロード時間をリセット
                self._reload = 0

        # リロード時間のカウント
        self._reload += 1

    ##
    # @brief 他のオブジェクトに衝突された場合の処理を行うメソッド
    #
    # @param damage 相手のオブジェクトから与えられるダメージ
    #
    # 他のオブジェクトから衝突された場合に,ヒットポイントの更新を行う.ヒットポイントが0以下の場合には自身のオブジェクトは消滅する.
    def collided(self, damage):
        self._hp -= damage
        if self._hp <= 0:
            self.kill()


##
# @brief Playerクラス
#
# 自機を表すクラスで,Airflameクラスを継承している.
class Player(Airflame):
    ##
    # @brief Playerクラスのコンストラクタ
    #
    # @param pos 自機の初期位置
    # @param pprop 自機の属性(静的なもの)
    # @param drawGroup spriteの描画を管理するGroupオブジェクト
    # @param bulletGroup 弾丸をまとめて管理するためのGroupオブジェクト
    def __init__(self, pos, pprop, drawGroup, bulletGroup):
        Airflame.__init__(self, pos, pprop, drawGroup, bulletGroup)

    ##
    # @brief 自機状態の更新メソッド
    #
    # @param command 自機の次の行動をまとめたオブジェクト
    #
    # commandの内容に基づいて次の行動を決定し，移動および弾丸の発射を行う.
    def update(self, command):
        self._nextAction(command)
        self._move()
        self._shot()

    ##
    # @brief commandの内容に基づいて次の行動を決定するメソッド
    #
    # @param command 自機の次の行動をまとめたオブジェクト
    #
    # commandの内容に基づいて移動速度(移動方向)と弾丸を発射するかを決定する.
    def _nextAction(self, command):
        self._v = command.v
        self._isShot = command.isShot

    # @brief 画面内を移動するメソッド
    #
    # 画面内を移動するメソッド，画面端ではループするようになっている
    def _move(self):
        super(Airflame, self)._move()
        self.rect.x %= SIZE[0]
        self.rect.y %= SIZE[1]


##
# @brief Enemyクラス
#
# 敵機を表すクラスで,Airflameクラスを継承している.
class Enemy(Airflame):
    # @param pos 自機の初期位置
    # @param pprop 自機の属性(静的なもの)
    # @param drawGroup spriteの描画を管理するGroupオブジェクト
    # @param bulletGroup 弾丸をまとめて管理するためのGroupオブジェクト

    ##
    # @brief Enemyクラスのコンストラクタ
    #
    # @param pos 敵機の初期位置
    # @param bprop 敵機の属性(静的なもの)
    # @param drawGroup spriteの描画を管理するGroupオブジェクト
    # @param bulletGroup 弾丸をまとめて管理するためのGroupオブジェクト
    # @param enemyGroup 敵機をまとめて管理するためのGroupオブジェクト
    def __init__(self, pos, bprop, drawGroup, bulletGroup, enemyGroup):
        Airflame.__init__(self, pos, bprop, drawGroup, bulletGroup)
        super(Airflame, self).add(enemyGroup)
        rx = random.randrange(-3, 3)
        ry = random.randrange(-3, 3)
        self._v = [rx, ry]

    ##
    # @brief 敵機状態の更新メソッド
    #
    # 現在の状態に基づいて次の行動を決定し，移動および弾丸の発射を行う.
    def update(self):
        self._nextAction()
        self._move()
        self._shot()

    ##
    # @brief 現在の状態に基づいて次の行動を決定するメソッド
    #
    # 現在の状態に基づいて移動速度(移動方向)と弾丸を発射するかを決定する.
    def _nextAction(self):
        isOutOfRange = checkOutOfRange(self.rect)
        if isOutOfRange[0]:
            self._v[0] *= -1
        if isOutOfRange[1]:
            self._v[1] *= -1

        r = random.random()
        if r < self.prop.shotFreq:
            self._isShot = True
        else:
            self._isShot = False

    ##
    # @brief 衝突したオブジェクト(Playerオブジェクト)に対してダメージを与えるメソッド
    #
    # @param player 自機
    #
    # 衝突したオブジェクトに対して直接ぶつかってダメージを与える.なお,衝突した後は敵機自身は消滅する.
    def damage(self, player):
        player.collided(self._hp)
        self.kill()


##
# @brief 自機への命令を処理するクラス
#
# キー入力を元に,自機への命令を決定する.
class Command(object):
    ## 移動量
    _D = 2
    ## キーと移動方向を対応付ける辞書
    _commandList = {
        pygame.K_UP: (0, -_D),
        pygame.K_RIGHT: (_D, 0),
        pygame.K_DOWN: (0, _D),
        pygame.K_LEFT: (-_D, 0),
    }
    ## 弾丸を発射するキー
    _SHOT_KEY = pygame.K_SPACE
    ## 速度と弾丸を発射可能かを保持する命令オブジェクト
    _command = collections.namedtuple('command', 'v isShot')

    ##
    # @brief キー入力を元に自機への命令を出力するメソッド
    #
    # @return 命令をまとめたオブジェクト(_commandオブジェクト)
    def getCommand(self):
        vx = 0
        vy = 0
        isShot = False
        pressed_keys = pygame.key.get_pressed()
        for key in Command._commandList.keys():
            if pressed_keys[key]:
                mvCommand = Command._commandList[key]
                vx += mvCommand[0]
                vy += mvCommand[1]
        if pressed_keys[Command._SHOT_KEY]:
            isShot = True

        com = Command._command((vx, vy), isShot)
        return com
