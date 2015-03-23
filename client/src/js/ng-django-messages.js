(function(angular, undefined) {
'use strict';

angular
	.module('ng.django.messages', [])
	.constant('djngMessagesEvents', djngMessagesEvents())
	.factory('djngMessagesSignal', djngMessagesSignal)
	.factory('djngMessagesInterceptor', djngMessagesInterceptor)
	.factory('djngMessagesModel', djngMessagesModel);



function djngMessagesEvents() {
	
	return Object.freeze({
		
		MESSAGES_UPDATED: 'djngMessagesEvents.MESSAGES_UPDATED',
		MESSAGES_CLEARED: 'djngMessagesEvents.MESSAGES_CLEARED'
	});
}


function djngMessagesSignal($rootScope, djngMessagesEvents) {
	
	return {
		
		messagesUpdated: messagesUpdated,
		onMessagesUpdated: onMessagesUpdated,
		messagesCleared: messagesCleared,
		onMessagesCleared: onMessagesCleared
	};
	
	/* --------------------- */
	
	function messagesUpdated(model) {
		
		$rootScope.$broadcast(djngMessagesEvents.MESSAGES_UPDATED, model);
	}
	
	function onMessagesUpdated(scope, handler) {
		
		scope.$on(djngMessagesEvents.MESSAGES_UPDATED, function (event, model) {
            handler(model);
        });
	}
	
	function messagesCleared() {
		
		$rootScope.$broadcast(djngMessagesEvents.MESSAGES_CLEARED);
	}
	
	function onMessagesCleared(scope, handler) {
		
		scope.$on(djngMessagesEvents.MESSAGES_CLEARED, function (event) {
            handler();
        });
	}
}


function djngMessagesInterceptor(djngMessagesModel) {
	
	return {
		response: response
	}
	
	/* ------------------- */
	
	function response(response) {

		if(containsMessages(response)) {
			
			djngMessagesModel.addMessages(response.data.django_messages);
			response.data = response.data.data;
		}
		
		return response;
	}
	
	function containsMessages(response) {
		
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


function djngMessagesModel(djngMessagesSignal) {
	
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
		
		djngMessagesSignal.messagesUpdated(_api);
	}
	
	function getMessages(clear) {
		
		if(!_messages)
			return [];
		
		if(clear || angular.isUndefined(clear)) {
			
			var msgs = _messages;
			_messages = [];
			_api.count = 0;
			
			djngMessagesSignal.messagesCleared();
			
			return msgs;
		}
		
		return _messages.concat();
	}
}

})(window.angular);