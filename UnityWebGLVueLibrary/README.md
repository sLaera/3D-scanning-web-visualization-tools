# UnityComponent

UnityComponent is a Vue component designed to embed Unity WebGL builds into a Vue.js project. It provides an interface for two-way interaction between the Vue application and the Unity instance.

## Features

- 🧩 Easily integrate Unity WebGL builds in Vue projects.
- 🔄 Two-way communication between the Vue app and Unity instance.
- 📡 Built-in event system for loading progress, success, and error handling.

## Example

- Example of UnityComponent usage
    
    ```vue
    <script setup lang="ts">
    import {UnityComponent, UnityChannel } from 'unity-webgl-vue'
    import type { UnityConfigs } from 'unity-webgl-vue'
    import { ref, watch } from 'vue'
    
    const channel = ref<UnityChannel | null>(null) 
    let buildUrl = './UnityProject'
    const unityConfigs: UnityConfigs = {
      dataUrl: buildUrl + '/project.data',
      frameworkUrl: buildUrl + '/project.framework.js',
      codeUrl: buildUrl + '/project.wasm',
      loaderUrl: buildUrl + '/project.loader.js'
    }
    
    function beforeLoad() {
      console.log('---BEFORE LOAD---')
    }
    
    function progress(p: number) {
      console.log('---PROGRESS---', p)
    }
    //the load event will generate the channel for the comunication with Unity 
    function loaded(c: UnityChannel) {
      console.log('---LOADED---', c)
      channel.value = c
    }
    //watch for the channel to be initialized
    //The channel will be null before the load event is emitted
    watch(channel, (channel) => {
      if(!channel)
        return
      //Example of reciving a Unity event
      channel.subscribe(
        'HelloJS',
        () => {
          alert('Game Start')
        },
        true
      )
    })
    
    function error(err: Error) {
      console.log('---ERROR---', err)
    }
    //example of calling an Unity function
    function createCube() {
      channel.value?.call('floor', 'Spawn', 2)
    }
    //example of quitting the Unity Instance
    function quit() {
      if (!channel.value) return
      channel.value.quit()
    }
    </script>
    
    <template>
      <div v-if="channel?.isActive" style="display: flex">
        <div style="width: 80%">
          <UnityComponent
            :unityConfigs="unityConfigs"
            width="100%"
            height="650px"
            @beforeLoad="beforeLoad"
            @progress="progress"
            @loaded="loaded"
            @error="error"
          />
        </div>
        <div style="width: 20%">
          <button @click="quit">Quit</button>
          <br />
          <button @click="createCube">New Cube</button>
        </div>
      </div>
      <div v-else>
        <h3>Unity instance is closed</h3>
      </div>
    </template>
    ```
    

## Usage

- **Core concepts**
    
    The component will load the Unity instance based on the provided configuration.
    
    It will emit several events during the loading process. At the end, it will emit a `loaded` event along with the Unity channel associated with the instance.
    
    The channel will manage communication with Unity. Events coming from Unity are handled using a publish-subscribe paradigm:
    
    - Unity publishes the events
    - The Vue application subscribes to them
    
    The channel also handles communication from Vue to Unity, making it possible to call a C# method from JavaScript.
    

There are a few steps to follow to ensure the component works correctly:

- **Build Unity Project**
    
    Make sure you have built your Unity project for WebGL correctly.
    
    The build process will generate the following files in the build folder (chosen before the build starts):
    
    ```
    Build
    |- Project.data
    |- Project.framework.js
    |- Project.wasm
    |- Project.loader.js
    ```
    
    The example above is referred to a development build. Production build produces slightly different files.
    
- **Use the component in the Vue application**
    
    You can use `UnityComponent` as shown below:
    
    ```html
    <UnityComponent
      :unityConfigs="{
        dataUrl: '/Build/Project.data',
        frameworkUrl: '/Build/Project.framework.js',
        codeUrl: '/Build/Project.wasm',
        loaderUrl: '/Build/Project.loader.js'
      }"
      width="950px"
      height="600px"
      @beforeLoad="onBeforeLoad"
      @progress="onProgress"
      @loaded="onLoaded"
      @error="onError"
    />
    ```
    

### Props

| Prop Name | Type | Default | Description |
| --- | --- | --- | --- |
| `unityConfigs` | [`UnityConfigs`](#unityconfigs) | `null` | Unity configuration object for initializing the instance |
| `width` | `string | number` | `'100%'` | Width of the canvas element |
| `height` | `string | number` | `'100%'` | Height of the canvas element |
| `tabindex` | `string | number` | `-1` | Tab index of the canvas element |

### Events

| Event Name | Payload                             | Description |
| --- |-------------------------------------| --- |
| `beforeLoad` | `null`                              | Triggered before the Unity instance starts loading |
| `progress` | `number`                            | Reports the loading progress as a value between 0 and 1 |
| `loaded` | [`UnityChannel`](#unitychannel-api) | Triggered when the Unity instance has been successfully loaded |
| `error` | `Error`                             | Triggered when there is an error during the loading process |

## Two way communication

The `UnityChannel` object retrieved from the `load` event will be used for comunicate with Unity

### Call Unity functions from Vue

```tsx
<script setup lang="ts">
const unityConfigs = {...}
function loaded(channel: UnityChannel) {
	//the return value of the function will always be ignored
	channel.call('ObjectName', 'functionName', ...params);
}
</script>
<template>
	<UnityComponent
        :unityConfigs="unityConfigs"
        width="100%"
        height="100%"
        @loaded="loaded"
    />
</template>
```

### Call Vue functions from Unity

**In Unity**

- Create a .jslib file in the asset folder of the Unity project (e.g. `./Plugin/js_comunication.jslib` )
    - this file will be used as a middleware to comunicate from C# to Vue
- Insert a function in the file following this structure:
    
    ```jsx
    //js_comunication.jslib
    
    mergeInto(LibraryManager.library, {
      // This is your function on the Unity side
      GreetJs: function (str) {
    	  /*
    	  * This is an example of a function that takes a string parameter (from c# side).
    	  * The string parameter must be converted to be used in JS.
    	  * For more information on how to convert different parameter types:
    	  * https://docs.unity3d.com/Manual/web-interacting-code-example.html
    	  */
        var data = UTF8ToString(str);
        
        /*
        * _UNITY_CHANNEL is a global variable created by the vue component.
        * The name of the channel can be changed by passing a configuration object 
        * with an initialized channelName property to the Vue component.
        */
        if (!window._UNITY_CHANNEL) {
    		    // This should not happen. The channel name should always be initialized when 
    				// the Unity instance is loaded.
    				// If this happens, make sure the channel name matches the one in the configuration object.
            console.error('cannot publish events. _UNITY_CHANNEL is not defined')
            return
        }
        
        /**
    		* Publishes an event, executing all callbacks associated with the given event name.
    		* Returns the value of the last executed callback.
    		*
    		* This method is the only method of UnityGlobalChannel intended 
    		* to be executed the jslib file. Any other methon should not be executed here.
    		*
    		* @param {EventName} eventName - The name of the event to publish.
    		* @param {...any[]} args - arguments passed to the callback functions.
    		* @returns {any} - Returns the value of the last callback executed.
    		*/
        let lastValue = window._UNITY_CHANNEL.publish('HelloJS', str);
        //It is possible to return back to C# a value
        return lastValue 
      },
    });
    ```
    
- you can call the function defined in .jslib file in C# scripts:
    
    ```csharp
    //NewBehaviourScript.cs
    
    using UnityEngine;
    using System.Runtime.InteropServices;
    
    public class NewBehaviourScript : MonoBehaviour {
    
      [DllImport("__Internal")]
      private static extern void GreetJs(string str);
    
      void Start() {
        GreetJs("This is a string.");
      }
    }
    ```
    

**In Vue**

Subscribe a method to the event defined in the .jslib file (in the example is `'HelloJS'`).

There could be multiple subscribers to the same event

```html
<script setup lang="ts">
const unityConfigs = {...}
function loaded(channel: UnityChannel) {
	channel.subscribe('HelloJS', (str) => {
    console.log(str);
    return 'Hi C#'
  });
}
</script>
<template>
	<UnityComponent
        :unityConfigs="unityConfigs"
        width="100%"
        height="100%"
        @loaded="loaded"
    />
</template>
```

## UnityChannel API

Class representing a communication channel between JavaScript and Unity.  Provides methods to send messages to Unity objects and receive events from the Unity instance.

### Methods

| Method                                  | Parameters                                                                                                                                                                                      | Description                                           | Returns         |
|-----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|-----------------|
| `call(objectName, methodName, params)`  | `objectName: string`: The Unity object name.<br>`methodName: string`: The method to call.<br>`params?: any`: Optional parameters to pass to the method.                                         | Calls a method on a Unity object.                     | `void`          |
| `setFullscreen(idFullscreen)`           | `isFullscreen: boolean`: If true, Unity will switch to fullscreen; if false, Unity will exit fullscreen.                                                                                        | Sets Unity to fullscreen mode or exits fullscreen.    | `void`          |
| `subscribe(eventName, callback, once?)` | `eventName: EventName`: The event to subscribe to.<br>`callback: Callback`: The function to execute when the event is triggered.<br>`once?: boolean`: Runs the callback once (default `false`). | Subscribes a callback to an event from Unity.         | `void`          |
| `unsubscribe(eventName, callback)`      | `eventName: EventName`: The event to unsubscribe from.<br>`callback: Callback`: The function to remove from the event.                                                                          | Unsubscribes a callback from an event.                | `void`          |
| `quit()`                                | None                                                                                                                                                                                            | Quits the Unity instance and clears all subscriptions | `Promise<void>` |

### Properties for `UnityChannel` Class

| Property   | Type      | Description                                   |
|------------|-----------|-----------------------------------------------|
| `isActive` | `boolean` | Returns whether the Unity instance is active. |

## UnityConfigs

Unity configuration object for initializing the instance.

You can find more details in the unity docs (https://docs.unity3d.com/Manual/webgl-templates.html)

<aside>
💡 Use unique channel names to manage multiple Unity projects at the same time
</aside>

| Property                     | Type      | Description                                                                                                                                                            | Required |
|------------------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `channelName`                | `string`  | Name of the global communication channel with Unity (default: `_UNITY_CHANNEL`).                                                                                       | No       |
| `loaderUrl`                  | `string`  | URL to the Unity WebGL loader script                                                                                                                                   | Yes      |
| `dataUrl`                    | `string`  | URL to the Unity WebGL data file                                                                                                                                       | Yes      |
| `frameworkUrl`               | `string`  | URL to the Unity WebGL framework file                                                                                                                                  | Yes      |
| `codeUrl`                    | `string`  | URL to the Unity WebGL code file                                                                                                                                       | Yes      |
| `memoryUrl`                  | `string`  | URL to the Unity WebGL memory file                                                                                                                                     | No       |
| `symbolsUrl`                 | `string`  | URL to the Unity WebGL symbols file for debugging                                                                                                                      | No       |
| `streamingAssetsUrl`         | `string`  | URL for accessing streaming assets                                                                                                                                     | No       |
| `companyName`                | `string`  | Name of the company that owns the Unity project                                                                                                                        | No       |
| `productName`                | `string`  | Name of the Unity product                                                                                                                                              | No       |
| `productVersion`             | `string`  | Version of the Unity product                                                                                                                                           | No       |
| `devicePixelRatio`           | `number`  | Sets the device pixel ratio for the canvas rendering                                                                                                                   | No       |
| `matchWebGLToCanvasSize`     | `boolean` | Whether WebGL should match the canvas size. If true (or unset), Unity synchronizes the WebGL canvas render target size with the DOM size of the canvas                 | No       |
| `autoSyncPersistentDataPath` | `true`    | If true, all file writes in the `Application.persistentDataPath` directory automatically persist across sessions. Otherwise, you must manually sync file modifications | No       |
| `webglContextAttributes`     | `object`  | WebGL context attributes for fine-tuning the WebGL context                                                                                                             | No       |

## Mouse and Keyboard focus

By default, Unity capture all keyboard input and set the cursor to be sticky.

This means that all keyboard input on the Vue application is captured by the Unity Application instead.

To mitigate this the `UnityComponent` sets by default `tabindex` to be -1 (it is possible to change this value by passing a `tabindex` prop to the component).

In order for this to work, Capture All Keyboard Input has to be set to false within your Unity Application. Preferably as soon as the Application is loaded.
<aside>
💡If the sticky cursor behavior is not wanted, set `WebGLInput.stickyCursorLock = false`.
This means that clicking to the Unity Instance doesn’t take control of the mouse
</aside>

**In Unity**

```cs
using UnityEngine;

public class GameController : MonoBehaviour {
  private void Start () {
#if UNITY_WEBGL == true && UNITY_EDITOR == false
    WebGLInput.captureAllKeyboardInput = false;
    //Uncommet to disable sticky behavior
    //WebGLInput.stickyCursorLock = false;
#endif
  }
}
```

## Handling multiple Unity instances at the same time

Due to how the events from Unity are handled, there could be some issues when loading multiple instances in the same page.

In a nutshell the channel accessed in the `.jslib` file in Unity is a global channel, so every Unity Instances could subscribe to the same channel creating conflicting events.

### Different Unity project

To make sure that the events don’t conflict a different channel name per instance is needed.

Set a channel name in the config passed as a prop:

**In vue:**

```html
<script setup lang="ts">
const unityConfigs1: UnityConfigs = {
	channelName: '_FIRST_PROJECT_'
  ...
}

const unityConfigs2: UnityConfigs = {
	channelName: '_SECOND_PROJECT_'
  ...
}
</script>

<template>
	<UnityComponent
	  :unityConfigs="unityConfigs1"
	  ...
	/>
	<UnityComponent
	  :unityConfigs="unityConfigs2"
	  ...
	/>
</template>
```

**In .jslib file in Unity:**

```js
//first project
mergeInto(LibraryManager.library, {
  example: function (str) {
	  //in this project you should use only the assinged channel name (_FIRST_PROJECT_)
    window._FIRST_PROJECT_.publish('example', str)
  },
});
```

```js
//second project
mergeInto(LibraryManager.library, {
  example: function (str) {
	  //in this project you should use only the assinged channel name (_SECOND_PROJECT_)
    window._SECOND_PROJECT_.publish('example', str)
  },
});
```

### Multiple instances of the same project

In this case it’s not possible to use different channel names.

A solution could be to send to Unity (as soon as the Unity instance is loaded) a postfix/prefix to use when publishing events.

**In Vue:**

```js
...
function load(channel){
	//send the postfix to Unity
	channel.call("JSCommunicationHandler", "SetEventPostfix", postfix)
	
	//listen for events with the postfix added to the event name
	channel.subscribe('HelloJS' + postfix, () => { alert('Game Start') })
}
...
```

**In Unity:**

Create a singleton class and assign it to an object called `JSCommunicationHandler` :

```cs
public class JsCommunicationHandler : MonoBehaviour
{
    public static JsCommunicationHandler Instance { get; private set; }

    public string JsEventPostfix { get; private set; }

		//singleton
    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(this);
        }
        else
        {
            Instance = this;
        }
    }

    private void SetEventPostfix(string postfix)
    {
		    //this function will be called by vue as soon as the Unity Instance start
        JsEventPostfix = postfix;
    }

}
```

Now every time you create a function in .jslib you should add a postfix parameter:

```jsx
//.jslib
mergeInto(LibraryManager.library, {
  HelloJS: function (postfix) {
    postfix = UTF8ToString(postfix);
    window._UNITY_CHANNEL.publish('HelloJS' + postfix);
  },
});
```

And every time you call the method in C# you have to use the singleton to set the postfix parameter:

```cs
//in a Unity script
public class NewMonoBehaviour: MonoBehaviour
{
	[DllImport("__Internal")]
	private static extern void HelloJS(string postfix);
	
	private void Start()
  {
	  //get the postfix from the singleton
	  //Vue should already have sent the postfix to Unity
		HelloJS(JsCommunicationHandler.Instance.JsEventPostfix);
  }
}
```