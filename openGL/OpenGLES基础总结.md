## OpenGLES 总结

### GLSL语言

#### 定义

[修饰符]  [精度]  [基本类型]  [定义的变量名]

#### 修饰符

none： 可读可写，默认可省略

const：只读，不能修饰结构体中的变量

attribute：全局只读，只能在vertex shader中使用，能与浮点，向量，矩阵结合使用

uniform：全局只读，在着色结束前不会改变，可与任意基本类型组合

varying：vertex shader 和 fragment shader信使

一般在vertex中设置，fragment中使用，fragmemt不能修改

invariant 保证在不同的着色器中精度相同

#### 精度

lowp 低精度

mediump 中精度

highp 高精度

* 不同的精度运算取精度最高的
* 片元着色器使用浮点型，必须指定浮点精度

```glsl
precision mediump float;
```

通过precision指定默认精度

#### 基本类型

void，boolean，float，int

vec2，vec3，vec4  2/3/4维浮点数向量

bvec2，bvec3，bvec4  2/3/4维布尔向量

ivec2，ivec3，ivec4   2/3/4维整型向量

mat2，mat3，mat4  2/3/4维浮点矩阵

sampler2D 2D纹理

samplerCube 立方体纹理，有6个面，每个面都是一个2D纹理

#### 访问

* 按照坐标系访问：vec.xyzw
* 按照颜色访问：vec.raba
* 未知：vec.stpq
* 按照下标访问：vec[0]

vec.x = vec.r = vec.s = vec[0]

#### 运算

* float 和 int

只支持同类型运算

需先转换后运算

强制转换：int(1.0) / float(2)

* 逐分量运算

vec2(1.0,2.0,3.0) * 2.0 = vec2(2.0,4.0,6.0)

mat2(1.0,1.0,1.0,1.0) * 2.0 = vec2(2.0, 2.0, 2.0, 2.0)

vet/mat是浮点类型，不能和int运算

#### 函数

* 函数不能递归调用
* 不能嵌套
* 如果无返回值，需要加void

#### 函数参数 限定符

in：默认，可读不可写，值传递，修改形参不会影响到实参

out：可写不可读，修改形参会改变实参

Inout： 可写可读，修改形参会改变实参

## OpenGLES 基本概念

### 清除窗口

#### 设置颜色缓存清楚值

glClearColor (red, blue, green, alpha)

GLES20.glClear(GLES20.GL_COLOR_BUFFER_BIT) ;清除,指定为颜色缓存

#### 设置深度缓冲清除值

glClearDepth(maxDepth)  范围：[0,1]

GLES20.glClear(GLES20.GL_DEPTH_BUFFER_BIT);清除,指定为深度缓存

深度缓存映射的是z轴，对应的的是视觉坐标系，反映片段距离眼睛的距离，大于maxDepth的部分不会被显示

#### 其他

GL_COLOR_BUFFER_BIT 颜色缓冲区

GL_DEPTCH_BUFFER_BIT 深度缓冲区

GL_ACCUM_BUFFER_BIT  累计缓冲区

GL_STENCIL_BUFFER_BIT  模版缓冲区

### 深度测试

深度就是3D像素点距离摄像机的距离，深度缓存存储着每个像素点的深度值

如果不使用深度测试，就需要控制绘制的顺序，需要先绘制距离摄像机远的，再绘制距离摄像机近的，否则距离摄像机远的像素可能会覆盖否则距离摄像机近的像素。

开启深度缓存后绘制顺序就不是那么重要了

#### 使用流程

1. 在onSurfaceCreated 中调用 GLES20.glEnable(GLES20.*GL_DEPTH_TEST*)，开启深度测试。

2. 在onDrawFrame 调用 GLES20.glClear(GLES20.*GL_DEPTH_BUFFER_BIT*)指定为深度缓存。

3. glDepthFunc 可以修改默认测试方式

   * GL_LESS（小于）；默认

   - GL_NEVER（没有处理）

   - GL_ALWAYS（处理所有）

   - GL_LEQUAL（小于等于）

   - GL_EQUAL（等于）

   - GL_GEQUAL（大于等于）

   - GL_GREATER（大于）

   - GL_NOTEQUAL（不等于）

### 混色 Blend

#### 透明

alpha 为0.6的物体由60%的自身颜色加%40背后物体颜色组成

alpha 为0.0的物体是完全透明的，颜色是100%背后物体的颜色

#### 混色

![](images/blend_img.png)

目标(destination)：先渲染的颜色，或叫已经渲染好的颜色

源(source)：后渲染的颜色，或叫现在正要渲染的颜色

#### glBlendFuncSeparate(GLenum srcRGB,GLenum dstRGB,GLenum srcAlpha,GLenum dstAlpha)

srcRGB 源颜色向量

dstRGB 目标颜色向量

srcAlpha 源透明因子

dstAlpha 目标透明向量

Color(result) = srcRGB * srcAlpha + dstRGB * dstAlpha

#### glBlendFunc(GLenum Source_factor, GLenum Destination_factor)

Source_factor 源透明因子

Destination_factor 目标透明向量

#### **glBlendEquation**(   GLenum *mode*)

设置源和目标的混合方程式

* **GL_FUNC_ADD**：Ar = As*sA + Ad*dA
* **GL_FUNC_SUBTRACT**：Ar = As*sA - Ad*dA
* **GL_FUNC_REVERSE_SUBTRACT**：Ar = Ad*dA - As*sA

### 坐标系统

![](images/coordinate_img.png)

如图：

在立体几何坐标中绘制绘制一个点的位置，需要x，y，z三个坐标的值

openGL将绘制好的坐标值转换成实际绘制坐标值，需要一系列类似流水线的转换

1. Local Space(局部空间) 它是相对于单独一个模型的坐标系

   如：一个平面三角形坐标

   ```kotlin
   floatArrayOf(
           0f,0.5f,0f,
           -0.5f,-0.5f,0f,
           0.5f,-0.5f,0f
       )
   ```

2. Model Matrix(模型矩阵) 它能将局部坐标转换为世界坐标，模型矩阵是一种变换矩阵，它能通过对物体进行位移、缩放、旋转来将它置于它本应该在的位置或朝向。

   **旋转：**

   做一个从(0,0,0)到(x,y,z)的向量，右手握住向量，大拇指指向向量正方向，四指环绕方向就是旋转方向

   ```kotlin
   Matrix.rotateM(modelMatrix,offset,angle,x,y,z)
   ```

   **平移**

   向x/y/z方向移动x/y/z个单位

   ```kotlin
   Matrix.translateM(modelMatrix,offset,x,y,z)
   ```

3. World Space(世界空间) 顶点相对于世界(整个程序)的坐标

4. View Matrix(视图矩阵) 将世界坐标转换成观测坐标

   ```kotlin
   Matrix.setLookAtM(viewMatrix,offset,eyeX,eyeY,eyeZ,centerX,
   centerY,centerZ,upX,upY,upZ)
   ```

   在eyeX,eyeY,eyeZ位置放置摄像机，摄像机的头部指向upX,upY,upZ,

   在centerX,centerY,centerZ位置放置观察物体

5. View Space(观测空间) 摄像机前方观测到的空间

6. Projection Matrix(投影矩阵) 将观测坐标转换为裁剪坐标

   ![](images/ortho_img.png)

   ```kotlin
   Matrix.orthoM(projectMatrix,left,right,radio,bottom,top,near,far)
   ```

   正交投影会创建一个立方体的视景体，视景体外的像素点就会被剪辑掉

   因为正交投影采用的是平行投影，所以不会产生近大远小的效果

   

   ![](images/frustum_img.png)

   ```kotlin
   Matrix.orthoM(projectMatrix,left,right,radio,bottom,top,near,far)
   ```

   透视投影会产生一个类似锥体的视景体，会尝试近大远小的效果

   * **W分量**

   openGL除了xyz外，还有w分量，默认为1，正交投影不会改变w，透视投影会根据近大远小改变w分量的值。

   裁剪实际上就是用像素点的xyz分量和w比较，如果xyz任意分量绝对值小于w的绝对值，就会被裁剪

   * ### 透视除法

   透视除法，就是将 x、y、z 坐标分别除以 w 分量，得到新的 x、y、z 坐标，也叫**归一化设备坐标**。

7. Clip Space(裁剪空间) 经过透视变换后得到的坐标就是裁剪空间，裁剪空间坐标都是在一定范围内(通常[-1,1])

8. Screen Space(屏幕空间)

   OpenGL 会使用 *glViewPort* 函数来将归一化设备坐标映射到屏幕坐标

   这个过程称为视口变换

   ```
   glViewport(x,y,width,height)
   ```

   x,y指定窗口左下角位置

   width，height 宽高

#### 适应宽高比

默认情况下，局部空间、世界空间、观察空间、裁剪空间的坐标系都是重合的，都是以(0,0,0)为坐标原点。

归一化设备坐标假定的坐标空间是一个正方形，但手机屏幕的视口却是一个长方形，这样的话，就会有一个方向被拉伸。

解决：

1. 在投影时就把拉伸的情况考虑进去

投影前坐标空间是一个正方形，将正方形对应屏幕较短的一边缩窄，或者将正方形对应屏幕较短的一边拉长，之后将坐标映射到屏幕时就恢复正常的比例了

```kotlin
//height > width
Matrix.frustumM(projectMatrix,0,-1f,1f,-height/width,height/width,3f,7f)
```

