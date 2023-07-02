﻿#import typing
import bpy
from bpy.props import IntProperty,FloatVectorProperty, EnumProperty,FloatProperty
from bpy.types import Context, Event
from mathutils import *
#import math
#import gpu
#import gpu_extras.presets
from bpy.props import BoolProperty
from bpy_extras import view3d_utils
#import bgl
import blf


bl_info = {
	"name":"borntransformbywheel_ver02",
	"author":"tanatan",
	"version":(0.1),
	"blender":(3,0,0),
	"locaton":"Rigging",
	"description":" transform of born to  depth  direction by mouse wheel",
	"warnig":"",
	"support":'COMMUNITY',
	"wiki_url":"",
	"tracker_url":"",
	"category":"pose"
}

#リージョンとスペースを取得する関数
def get_region_and_space(context, area_type, region_type, space_type):
	region = None
	area = None
	space = None

	# 指定されたエリアの情報を取得する
	for a in context.screen.areas:
		if a.type == area_type:
			area = a
			break
	else:
		return (None, None)
	# 指定されたリージョンの情報を取得する
	for r in area.regions:
		if r.type == region_type:
			region = r
			break
	# 指定されたスペースの情報を取得する
	for s in area.spaces:
		if s.type == space_type:
			space = s
			break

	return (region, space)



def textdraw(context,event,target_point_world):
	j = 1
	print("textdraw")
	'''
	blf.size(0, 100, 72)
	blf.position(0,100,100,0)
	blf.draw(0, "hhhhhhhhhh")
	'''
	
	if not(dammy22.wacthvalue1 is None):
		for k1,k2 in dammy22.wacthvalue1.items():
			
			blf.size(0, 40, 72)
			blf.position(0,100,j*100,0)
			blf.draw(0, "("+str(k1)+"\n"+str(k2)+")")
			j = j +1
	

#ハンドルには一つの関数しか入れられないので一つにまとめる。
def drawhandlefunc(context,target_point_world,wheeldepth,event):
	textdraw(context,event,target_point_world)

#逆変換を求める関数
def matrixinvert(matrix):
	minv = matrix.copy()
	minv.invert()
	return minv

#動作チェック済み（正常）
#マウスをリージョン座標に変換する。
def vector_rigion_by_mouse(context,event):
	vm = Vector((event.mouse_region_x,event.mouse_region_y))
	return vm

#動作チェック済み
#親のcostumposeに依存した子のrestposebone座標（親カスタム子レスト）とlocal座標の位置ベクトルをrestpose座標変換する。
#第一引数pose座標に当たるposeボーンオブジェクト,第二引数変換したいローカル座標のベクトル
def convert_local_to_custumrestpose(aposebone,local_vector):
	local_to_custumpose = matrixinvert(aposebone.matrix)
	local_to_restpose = aposebone.matrix_basis @ local_to_custumpose
	return local_to_restpose @ local_vector

# TODO: 動作未チェック
#matrix_basisを単位行列でリセットしてからベクトルとローテーションを得る関数
#第一引数は回転したい方向ベクトル（ローカル座標）、第二引数はオブジェクトの基準方向（ローカル）、第三引数は回転させるオブジェクト
def restrotation(target_vector_local,obj_vector_local,obj):
	(l,q,s) = obj.matrix_basis.decompose()
	Matrix_rotation_reset = Matrix.LocRotScale(l,Quaternion((1.0,0.0,0.0,0.0)),s)
	obj.matrix_basis = Matrix_rotation_reset
	obj.rotation_mode = 'QUATERNION'
	q = obj_vector_local.rotation_difference(target_vector_local)
	obj.rotation_quaternion = q


# TODO: 動作未チェック
#ホイールのeventからdepthに加減する数値を割り出す。
def wheeleventpulse(event,depth):#最初は０が入る
	if event.value == 'PRESS':
			if event.type == 'WHEELUPMOUSE':
				return depth - 1
			if event.type == 'WHEELDOWNMOUSE':
				return depth + 1
			if event.type == 'MIDDLEMOUSE':
				return 0

	return depth


#オブジェクトを使ってテストをするためのクラス。Z軸マウスに追従する
class testdammy22(bpy.types.Operator):
	bl_idname = "test.testdammy22ver02"
	bl_label = "testdammy22ver02"
	bl_description = ""
	#bl_options = {'REGISTER','UNDO'}

	__modalrunning = False
	obj_sphere = None
	init_matrix_basis = None
	#invokeで初期化されている。
	depth = 0

	@classmethod
	def is_modalrunning(cls):
		return cls.modalrunning
	
	def execute(self,context):
		return {'FINISHED'}
	
	
	#モーダルモードの呼び出し
	def modal(self,context,event):
		print("run modal")

		region, space = get_region_and_space(context, 'VIEW_3D', 'WINDOW', 'VIEW_3D')


		#escキーで終了
		if event.type == 'ESC':
			print("Pushesc")
			testdammy22.__modalrunning = False
			return {'FINISHED'}
		
		#イベントからマウスのリージョン座標を取得
		mouseregion = vector_rigion_by_mouse(context,event)
		print(mouseregion)

		self.depth = wheeleventpulse(event,self.depth)
		
		#このあたりが何かおかしい,ローテーションの位置
		#マウスの位置のローカル座標ベクトルを取得(これはあっている確認済)
		vector_mouse_world = view3d_utils.region_2d_to_location_3d(region,space.region_3d,mouseregion,Vector((self.depth,0,0)))

		#マウスの座標
		mvec_local = self.init_matrix_basis @ vector_mouse_world
		self.obj_sphere.show_axis = True
		
		
		#restrotation(mvec,Vector((0,0,1)),self.obj_sphere)

		#第一引数が定数ベクトルだと上手く言っている。
		#restrotation(Vector((0,1,0)),Vector((0,0,1)),self.obj_sphere)
		restrotation(mvec_local,Vector((0,0,1)),self.obj_sphere)

		

		return {'RUNNING_MODAL'}
	
	# TODO: ここでrestの座標変換を変数に格納する。
	#最初の呼び出し
	def invoke(self, context, event):
		if context.area.type == 'VIEW_3D':
			
			if not self.is_modalrunning():
				
				# モーダルモードを開始
				testdammy22.__modalrunning = True
				mh = context.window_manager.modal_handler_add(self)
				#変数の初期化
				self.depth = 0
				bpy.ops.mesh.primitive_uv_sphere_add(radius= 1,location = Vector((0,0,0)),align='CURSOR')
				self.obj_sphere = bpy.context.active_object
				self.obj_sphere.rotation_mode = 'QUATERNION'
				
				self.init_matrix_basis = self.obj_sphere.matrix_world.copy()

				return {'RUNNING_MODAL'}
			
			else:
				#__modalrunningがtrueなら終了
				testdammy22.__modalrunning = False				
				return {'FINISHED'}
		
#マウスとホイールを使ってオブジェクトの位置を動かす。
class testdammy22_lcation(bpy.types.Operator):
	bl_idname = "test.testdammy22_location"
	bl_label = "testdammy22ver02_location"
	bl_description = ""
	#bl_options = {'REGISTER','UNDO'}

	__modalrunning = False
	obj_sphere = None
	mvec= Vector((0,0,0))
	init_matrix_basis = None
	#invokeで初期化されている。
	depth = 0

	@classmethod
	def is_modalrunning(cls):
		return cls.__modalrunning
	
	def execute(self,context):
		return {'FINISHED'}
	
	
	#モーダルモードの呼び出し
	def modal(self,context,event):
		print("run modal")

		region, space = get_region_and_space(context, 'VIEW_3D', 'WINDOW', 'VIEW_3D')

		#escキーで終了
		if event.type == 'ESC':
			print("Pushesc")
			testdammy22_lcation.__modalrunning = False
			return {'FINISHED'}
		
		#イベントからマウスのリージョン座標を取得
		mouseregion = vector_rigion_by_mouse(context,event)
		print(mouseregion)

		self.depth = wheeleventpulse(event,self.depth)
		
		#マウスの位置のローカル座標ベクトルを取得(これはあっている確認済)
		vector_world = view3d_utils.region_2d_to_location_3d(region,space.region_3d,mouseregion,Vector((self.depth,0,0)))

		#マウスのワールド座標上にオブジェクトの位置を移動
		self.obj_sphere.location = vector_world

		return {'RUNNING_MODAL'}
	
	# TODO: ここでrestの座標変換を変数に格納する。
	#最初の呼び出し
	def invoke(self, context, event):
		if context.area.type == 'VIEW_3D':
			
			if not self.is_modalrunning():
				
				# モーダルモードを開始
				testdammy22_lcation.__modalrunning = True
				mh = context.window_manager.modal_handler_add(self)
				#変数の初期化
				self.depth = 0
				bpy.ops.mesh.primitive_uv_sphere_add(radius= 1,location = Vector((0,0,0)),align='CURSOR')
				self.obj_sphere = bpy.context.active_object

				return {'RUNNING_MODAL'}
			else:
				#__modalrunningがtrueなら終了
				testdammy22_lcation.__modalrunning = False				
				return {'FINISHED'}
	
		
# TODO: #bone用テストクラス
class testdammy22_bone(bpy.types.Operator):
	bl_idname = "test.testdammy22_bonever02"
	bl_label = "testdammy22_bonever02"
	bl_description = ""
	#bl_options = {'REGISTER','UNDO'}

	__modalrunning = False	
	depth = 0	
	init_matrix_basis = None
	apbone = None

	#M:matrix,c:custum,r:rest,l:local,p:pose,larm:localarmature
	M_l_to_cpbone = None
	M_l_to_rpbone = None
	M_w_to_larm = None
	l = None

	@classmethod
	def is_modalrunning(cls):
		return cls.__modalrunning

	def execute(self,context):
		ap = bpy.data.objects["アーマチュア"].pose.bones[2]
		local_vector = Vector((0,0,3))

		cdv = convert_local_to_custumrestpose(aposebone=ap,local_vector=local_vector)
		bpy.ops.mesh.primitive_cube_add(location=cdv)

	def modal(self,context,event):
		
		region,space = get_region_and_space(context, 'VIEW_3D', 'WINDOW', 'VIEW_3D')
		#カスタムプロパティのためのsceneオブジェクトの取得
		scene = context.scene

		#escキーで終了
		if (event.type == 'ESC') or (event.type == 'LEFTMOUSE'):
			print("Pushesc")
			testdammy22_bone.__modalrunning = False
			return {'FINISHED'}
		
		#ホイールのイベントからデプス値を設定
		self.depth =  wheeleventpulse(event,self.depth)
		
		#解像度を掛け算
		d = scene.depthresolution * self.depth
		
		
		print("depth",scene.depthresolution)
		print("d",d)

		#イベントからマウスのリージョン座標を取得
		mouseregion = vector_rigion_by_mouse(context,event)
		#マウスの位置のローカル座標ベクトルを取得(これはあっている確認済)
		vector_mouse_world = view3d_utils.region_2d_to_location_3d(region,space.region_3d,mouseregion,Vector((d,0,0)))
		#ボーン座標上のy向き単位ベクトル
		vector_y = Vector((0,1,0))
		
		#ワールド座標からレストポーズ座標への変換行列を取得
		M_w_to_rpbone = self.M_l_to_rpbone @ self.M_w_to_larm

		#マウスのワールド座標ベクトルをレストポーズ座標へ変換
		V_m_rpbone = (M_w_to_rpbone @ vector_mouse_world) - self.l
		
		#ボーン座標のY軸方向ベクトルとマウスの座標ベクトルの回転を取得し回転。
		self.apbone.rotation_mode = 'QUATERNION'
		q = vector_y.rotation_difference(V_m_rpbone)
		self.apbone.rotation_quaternion = q

		#長さのスケールを変更
		if scene.LengthOption :
			self.apbone.scale.y = V_m_rpbone.length/vector_y.length
		

		print("rummodeal",mouseregion)
		return {'RUNNING_MODAL'}

	def invoke(self, context, event):

		if not self.is_modalrunning():
			# TODO: ここでレスト関数を取得				
			# モーダルモードを開始

			#初期化
			self.depth = 0
			

			testdammy22_bone.__modalrunning = True
			mh = context.window_manager.modal_handler_add(self)

			self.apbone = bpy.context.active_pose_bone
			self.M_l_to_cpbone = matrixinvert(self.apbone.matrix)
			self.M_l_to_rpbone = self.apbone.matrix_basis @ self.M_l_to_cpbone
			self.M_w_to_larm = matrixinvert(bpy.context.active_object.matrix_world)
			#ポーズモードのローテーションを取得する。
			(l,q,s) = self.apbone.matrix_basis.decompose()
			self.l = l

		
			
			return {'RUNNING_MODAL'}

		else:
			testdammy22_bone.__modalrunning = False				
			return {'FINISHED'}




class DAMMY22VER2_PT_PaneleObject(bpy.types.Panel):
	bl_label = "dammy22ver2"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "dammy22"
	bl_context = "posemode"


	def draw(self,context):
		
		layout = self.layout

		#カスタムプロパティをシーンオブジェクトに格納しているのでシーンオブジェクトの読み込み
		scene = context.scene

		layout.operator(testdammy22_bone.bl_idname, text="WLD")
		layout.prop(scene,"depthresolution",text = "depthresolution")
		layout.prop(scene,"LengthOption",text = "scale change")
		
def init_props():
    scene = bpy.types.Scene
    scene.depthresolution = FloatProperty(
        name="depthresolution",
        description="Distance moved in one wheel revolution",
        default=1,
        min=0,
        #max=500
    )

	#ボーンの長さを変えるかどうかのオプション、Falseにすると向きだけが変わるようになる。
    scene.LengthOption = BoolProperty(
        name="LengthOption",
        description="Whether to change the length",
        default=True
    )


def clear_props():
    scene = bpy.types.Scene
    del scene.depthresolution
    del scene.LengthOption

addon_keymaps = []

def register_shortcut():
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc:
            km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
            kmi = km.keymap_items.new(
            idname=testdammy22_bone.bl_idname,
            type='Q',
            value='PRESS',
            shift=True,
            ctrl=False,
            alt=False,
            )
        # ショートカットキー一覧に登録
        addon_keymaps.append((km, kmi))

def unregister_shortcut():
    for km, kmi in addon_keymaps:
    # ショートカットキーの登録解除
    # 引数
    #   第1引数: km.keymap_items.newで作成したショートカットキー
    #            [bpy.types.KeyMapItem]
        km.keymap_items.remove(kmi)
    # ショートカットキー一覧をクリア
    addon_keymaps.clear()
	


def menu_fn_pose(self,context):
	self.layout.separator()
	self.layout.operator(testdammy22_bone.bl_idname)

def menu_fn_object(self,context):
	self.layout.separator()
	self.layout.operator(testdammy22.bl_idname)
	self.layout.operator(testdammy22_lcation.bl_idname)


classes = [
	testdammy22,
	DAMMY22VER2_PT_PaneleObject,
	testdammy22_bone,
	testdammy22_lcation,
]


def register():
	for c in classes:
		bpy.utils.register_class(c)

	init_props()
	register_shortcut()
	bpy.types.VIEW3D_MT_pose.append(menu_fn_pose)
	bpy.types.VIEW3D_MT_object.append(menu_fn_object)


def unregister():
	unregister_shortcut()
	bpy.types.VIEW3D_MT_pose.remove(menu_fn_pose)
	bpy.types.VIEW3D_MT_object.remove(menu_fn_object)

	clear_props()
	for c in classes:
		bpy.utils.unregister_class(c)

if __name__ == "__main__":
	register()
