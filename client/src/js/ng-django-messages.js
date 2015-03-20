(function(angular, undefined) {
'use strict';

angular
	.module('ng.django.messages', [])
	.constant('djangoMessagesEvents', djangoMessagesEvents())
	.factory('djangoMessagesSignal', djangoMessagesSignal)
	.factory('djangoMessagesInterceptor', djangoMessagesInterceptor)
	.factory('djangoMessages', djangoMessages);



function djangoMessagesEvents() {
	
	return Object.freeze({
		
		MESSAGES_UPDATED: 'djangoMessagesEvents.MESSAGES_UPDATED',
		MESSAGES_CLEARED: 'djangoMessagesEvents.MESSAGES_CLEARED'
	});
}


function djangoMessagesSignal($rootScope, djangoMessagesEvents) {
	
	return {
		
		messagesUpdated: messagesUpdated,
		onMessagesUpdated: onMessagesUpdated,
		messagesCleared: messagesCleared,
		onMessagesCleared: onMessagesCleared
	};
	
	/* --------------------- */
	
	function messagesUpdated(model) {
		
		$rootScope.$broadcast(djangoMessagesEvents.MESSAGES_UPDATED, model);
	}
	
	function onMessagesUpdated(scope, handler) {
		
		scope.$on(djangoMessagesEvents.MESSAGES_UPDATED, function (event, model) {
            handler(model);
        });
	}
	
	function messagesCleared() {
		
		$rootScope.$broadcast(djangoMessagesEvents.MESSAGES_CLEARED);
	}
	
	function onMessagesCleared(scope, handler) {
		
		scope.$on(djangoMessagesEvents.MESSAGES_CLEARED, function (event) {
            handler();
        });
	}
}


function djangoMessagesInterceptor(djangoMessages) {
	
	return {
		response: response
	}
	
	/* ------------------- */
	
	function response(response) {

		if(containsDjangoMessages(response)) {
			
			djangoMessages.addMessages(response.data.django_messages);
			response.data = response.data.data;
		}
		
		return response;
	}
	
	function containsDjangoMessages(response) {
		
		return !!(contentTypeIsJson(response) &&
				  isNotArray(response.data) &&
				  !!(response.data.django_messages));
	}
	
	function contentTypeIsJson(response) {
		return response.headers('content-type') == 'application/json';
	}
	
	function isNotArray(obj) {
		return !(obj.constructor === Array);
	}
}


function djangoMessages(djangoMessagesSignal) {
	
	var _api,
		_messages;
	
	return _api = {
			
		addMessages: addMessages,
		getMessages: getMessages,
		count: 0	
	};
	
	/* -------------- */
	
	function addMessages(arr) {
		
		_messages = _messages || [];
		_messages = _messages.concat(arr);

		_api.count = _messages.length;
		
		djangoMessagesSignal.messagesUpdated(_api);
	}
	
	function getMessages(clear) {
		
		if(!_messages)
			return [];
		
		if(clear || angular.isUndefined(clear)) {
			
			var msgs = _messages;
			_messages = [];
			_api.count = 0;
			
			djangoMessagesSignal.messagesCleared();
			
			return msgs;
		}
		
		return _messages.concat();
	}
}

})(window.angular);