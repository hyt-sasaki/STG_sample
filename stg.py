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
# import random
# import collections


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
        self.v = [0, 0]

    ##
    # @brief 画面内を移動するメソッド
    #
    # self.vに基づいて移動を行う.
    def move(self):
        self.rect.move_ip(self.v[0], self.v[1])


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
        self.v = self.prop.v

    ##
    # @brief 状態の更新メソッド
    #
    # self.vに基づいて移動を行い，弾丸の状態を更新する
    def update(self):
        self.move()

    ##
    # @brief 衝突したオブジェクトに対してダメージを与えるメソッド
    #
    # @param airflame ダメージを与える対象となるオブジェクト
    #
    # 衝突したオブジェクトに対してダメージを与える.なお,衝突した後は弾丸自身は消滅する.
    def damage(self, airflame):
        airflame.collided(self.prop.d)
        self.kill()
