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
# import collections


## ゲーム画面のサイズ
SIZE = (640, 480)


##
# @brief Rectが画面外に出ていないかを判定する関数
#
# @param rect 判定対象となるRectオブジェクト
#
# @return 0番目がx座標,1番目がy座標が範囲外かどうかをbool値で保持するtupple
def checkOutOfRange(rect):
    x = rect.x
    y = rect.y
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
        self.__v = [0, 0]

    ##
    # @brief 画面内を移動するメソッド
    #
    # self.__vに基づいて移動を行う.
    def __move(self):
        self.rect.move_ip(self.__v[0], self.__v[1])


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
        self.__v = self.prop.v

    ##
    # @brief 状態の更新メソッド
    #
    # self.__vに基づいて移動を行い，弾丸の状態を更新する
    def update(self):
        self.__move()

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
        self.__hp = prop.hp
        ## 機体が弾丸を撃ってからの経過時間
        self.__reload = prop.reloadLimit
        ## 機体が弾丸を撃とうとしているかどうかを表すbool値
        self.__isShot = False

    ##
    # @brief 弾丸を発射するメソッド
    #
    # self.__isShotおよびself.__reloadの値が条件を満たしている場合に，弾丸を発射する.
    def __shot(self):
        if self.__isShot:
            if self.__reload > self.prop.reloadLimit:
                # 生成する弾丸の初期位置を設定
                bulletPos = self.rect.center
                # 生成する弾丸のプロパティを設定
                bulletProp = self.prop.bprop
                # 弾丸の生成
                Bullet(bulletPos, bulletProp, self.drawGroup, self.bulletGroup)
                # リロード時間をリセット
                self.__reload = 0

        # リロード時間のカウント
        self.__reload += 1

    ##
    # @brief 他のオブジェクトに衝突された場合の処理を行うメソッド
    #
    # @param damage 相手のオブジェクトから与えられるダメージ
    #
    # 他のオブジェクトから衝突された場合に,ヒットポイントの更新を行う.ヒットポイントが0以下の場合には自身のオブジェクトは消滅する.
    def collided(self, damage):
        self.__hp -= damage
        if self.__hp <= 0:
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
        self.__nextAction(command)
        self.__move()
        self.__shot()

    ##
    # @brief commandの内容に基づいて次の行動を決定するメソッド
    #
    # @param command 自機の次の行動をまとめたオブジェクト
    #
    # commandの内容に基づいて移動速度(移動方向)と弾丸を発射するかを決定する.
    def __nextAction(self, command):
        self.__v = command.v
        self.__isShot = command.isShot
