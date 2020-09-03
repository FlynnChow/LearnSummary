****感谢：https://juejin.im/post/5b1fbd796fb9a01e8c5fd847#heading-5
## RXJAVA 消息订阅
#### observable##create(ObservableOnSubscribe)//创建被观察者
create()主要做的事情就是把**ObservableOnSubscribe**封装成一个ObservableCreate对象，并且返回它。
ObservableCreate是Observable的具体实现类。
#### observable##subscribe(Observer)//订阅
subscribe()所做的事情就是将observer对象传入subscribeActual()方法中，subscribeActual()是一个抽象方法，由子类实现。这里默认调用它的就是ObservableCreate对象。
#### observableCreate##subscribeActual(Observer)
该方法首先将observer对象封装到CreateEmitter对象中，CreateEmitter实现了ObservableEmitter接口和Disposable接口。
然后调用了observer的onSubscribe(CreateEmitter)方法，接着调用了source的subscribe(CreateEmitter)方法，这里的source指的便是ObservableCreate封装的ObservableOnSubscribe对象，所以对用了create中定义方法。
最后在subscribe中通过传入的CreateEmitter又调用了它的onNext,onError,onComplete等方法。
## RXJAVA 线程调度
#### Schedulers
Schedulers是一个调度类,不同的调度的线程有不同的实现
如IoScheduler io调度类
NewThreadSchduler 新线程调度类
ComputationSchduler 计算型调度类
。。
#### schedulers.io()
它主要使用静态内部类的单列模式创建了一个IoSchduler对象并且返回
#### observable##subscribeOn(Schedulers)
它做的事就是把当前被观察者对象(this/ObservableCreate)和传入调度器(Schedulers)封装成一个ObservableSubscribeOn对象并且返回。

所以接下来的订阅(subscribe())中先调用的是ObservableSubscribeOn对象的subscribeActual(Observer)方法。
#### ObservableSubscribeOn##subscribeActual()
它首先会将传入的Observer对象封装成SubscribeOnObserver对象
然后调用Observer的onSubscribe方法，这里是没有任何线程调度代码，所以它默认运行在当前线程
接下来：
```
parent.setDisposable(scheduler.scheduleDirect(new SubscribeTask(parent)));
```
它先将SubscribeOnObserver对象封装成一个SubscribeTask对象，他是一个实现了Runnable接口的类，它的run方法执行的是source.subscribe(SubscribeOnObserver)方法，这里source通常指的是ObservableCreate，所以通过它又将方法传递到ObservableCreate的subscribe中。

scheduler.scheduleDirect，这里所做的就是线程调度。scheduler就是封装SubscribeOnObserver时引入的调度器，所以不同的调度器的scheduleDirect会产生不同的效果。
#### Scheduler##scheduleDirect()
这里首先会通过createWorker()方法得到一个Worker对象
##### createWorker()
它所做的就是返回一个EventLoopWorker对象
它的初始化中最重要的就是通过CacheWorkerPool对象个get()方法取得一个ThreadWorker对象
get()中如果缓存池不为空就会从中取得一个worder，否则就新建一个

##### worker##schedule(runnable,delay,timeUnit)
它主要就是使用了之前获得的ThreadWorker对象的scheduleActual方法。
scheduleActual()使用了线程池来完成runnable来执行runnable方法，之前runnable还会先被包装成ScheduleRunnable

接下来会到scheduler.scheduleDirect()方法
这里在获得Worker对象后，会将worker和runnable对象封装成DisposeTask对象，然后在执行worker的schedule方法并传入task对象。

#### 如果多次使用subscribeOn()只有第一次有效
如果多次使用subscribeOn()，只有将ObservableCreate多次包装，这样会多次在线程池中运行run方法来进入内侧，最后进入的还是第一次封装的，所以最后有效的线程调度还是第一次封装的

#### observable##observerOn(Schedulers)
该方法做的还是把当前上下文的Observable对象和Schduler对象封装成ObservableObserverOn对象。

#### ObservableObserverOn##subscribeActual()
这里有个判断
如果当前调度环境就是Scheduler所指，那就直接调用内部Observable的subscribe方法。
否则会
通过Schedule的createWorker()方法得到一个worker
Observer和worker对象封装成ObserveOnObserver对象，在调用subscribe方法。
ObserveOnObserver实现了Runnable接口，是一个Runnable对象
#### ObserveOnObserver#onNext#onComplete
会先将传入的消息存入消息队列中，在调用内部work的schedule()方法，传入的便是自己。

run方法执行的就是从消息队列取出消息，并且得到内部引用的observer对象，并且调用它的onNext/onComplete方法。

#### 切断消息
切断消息的步骤通常是在onSubscribe(Disposable)中获得Disposable对象，在next中调用它的dispose()方法取消订阅。这里传入的便是CreateEmitter对象。
所以Disposable的dispose具体实现就是在CreateEmitter中。
##### dispose()
dispose所做的主要就是DisposableHelper是一个枚举类，它的dispose方法来将当前的引用设置为DISPOSED。

之后被观察者还会继续进行任务，但是订阅者再也不会收到消息。

onNext 中会判断是否取消订阅
onComplete 中如果取消订阅就什么都不会做，否则它会通知观察者然后取消订阅
onError 如果取消订阅会报错，调用完后也会取消订阅

## map
map()方法用于变换，将观察的获得的对象变化成另一个对象

map

将function和当前上下被观察者封装成一个observablemap

在subscribeactual中，会对把观察者和fuction一起封装成新观察者mapobserver

在它的next中会先运行fuction把消息进行转换，再把转换后的消息放入下一个观察者的next方法执行。

flatmap
将function和当前上下被观察者封装成一个observableflatmap

在subscribeactual中，会对把观察者和fuction一起封装成新观察者mergebserver

在它的next中会先运行fuction把消息进行转换成新的被观察者，然后在传入subscribeinner()中执行。