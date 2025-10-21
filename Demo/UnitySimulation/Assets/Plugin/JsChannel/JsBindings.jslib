mergeInto(LibraryManager.library, {
    PublishEventJson: function (eventName, json, channelName) {
        eventName = UTF8ToString(eventName);
        channelName = UTF8ToString(channelName);
        
        dataStr = UTF8ToString(json);
        channelName = UTF8ToString(json);
        data = JSON.parse(dataStr);
        
        if (!window[channelName]) {
            console.error(`cannot publish events. ${channelName} is not defined`)
            return
        }
        window[channelName].publish(eventName, data);
    },
    PublishEventString: function (eventName, data, channelName) {
        eventName = UTF8ToString(eventName);
        channelName = UTF8ToString(channelName);
        
        dataStr = UTF8ToString(data);

        if (!window[channelName]) {
            console.error(`cannot publish events. ${channelName} is not defined`)
            return
        }
        window[channelName].publish(eventName, dataStr);
    },
    PublishEventNumber: function (eventName, data, channelName) {
        eventName = UTF8ToString(eventName);
        channelName = UTF8ToString(channelName);
        
        if (!window[channelName]) {
            console.error(`cannot publish events. ${channelName} is not defined`)
            return
        }
        window[channelName].publish(eventName, data);
    },
    PublishEventArray: function (eventName, array, size, channelName) {
        eventName = UTF8ToString(eventName);
        channelName = UTF8ToString(channelName);
        
        let vett = []
        for(var i = 0; i < size; i++)
            vett[i] = HEAPF32[(array >> 2) + i]
        
        if (!window[channelName]) {
            console.error(`cannot publish events. ${channelName} is not defined`)
            return
        }
        window[channelName].publish(eventName, vett);
    },
    PublishEventTexture: function (eventName, textureId, channelName) {
        eventName = UTF8ToString(eventName);
        channelName = UTF8ToString(channelName);
        
        if (!window[channelName]) {
            console.error(`cannot publish events. ${channelName} is not defined`)
            return
        }
        window[channelName].publish(eventName, GL.textures[textureId]);
    },
});