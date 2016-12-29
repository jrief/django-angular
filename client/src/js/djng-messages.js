(function(angular, undefined) {
'use strict';

angular
	.module('djng-messages', [])
	.constant('djngMessagesEvents', djngMessagesEvents())
	.factory('djngMessagesSignal', djngMessagesSignal)
	.factory('djngMessagesInterceptor', djngMessagesInterceptor)



function djngMessagesEvents() {

	return Object.freeze({
		MESSAGES_UPDATED: 'djngMessagesEvents.MESSAGES_UPDATED'
	});
}


function djngMessagesSignal($rootScope, djngMessagesEvents) {

	return {

		messagesUpdated: messagesUpdated,
		onMessagesUpdated: onMessagesUpdated
	};

	/* --------------------- */

	function messagesUpdated(messages) {

		$rootScope.$broadcast(djngMessagesEvents.MESSAGES_UPDATED, messages);
	}

	function onMessagesUpdated(scope, handler) {

		scope.$on(djngMessagesEvents.MESSAGES_UPDATED, function (event, messages) {
            handler(messages);
        });
	}
}


function djngMessagesInterceptor(djngMessagesSignal) {

	var _responders;

	return {
		response: response,
		addResponder: addResponder,
		removeResponder: removeResponder,
		clearResponders: clearResponders
	}

	/* ------------------- */

	function response(response) {

		if(_hasMessages(response)) {

			var messages = response.data.django_messages;

			_processResponders(messages);
			_dispatchSignal(messages);

			response.data = response.data.data;
		}

		return response;
	}

	/**
	 * @param value An object or array of objects with the following interface
	 *
	 * addMessages(value)
	 */
	function addResponder(value) {
		_responders = _responders || [];
		_responders = _responders.concat(value);
	}

	function removeResponder(value) {
		if(_responders) {
			var ind = _responders.indexOf(value);
			if(ind != -1) {
				_responders.splice(ind, 1);
			}
		}
	}

	function clearResponders() {
		_responders = null;
	}

	function _hasMessages(response) {

		return _contentTypeIsJson(response) &&
			   _dataIsNotArray(response.data) &&
			   _dataContainsMessages(response.data);
	}

	function _contentTypeIsJson(response) {
		return response.headers('content-type') === 'application/json';
	}

	function _dataIsNotArray(data) {
		return !angular.isArray(data);
	}

	function _dataContainsMessages(data) {
		return !!data.django_messages;
	}

	function _processResponders(messages) {

		if(_responders) {

			var i = 0,
				len = _responders.length;

			for(; i < len; i++) {
				_responders[i].addMessages(messages);
			}
		}
	}

	function _dispatchSignal(messages) {
		djngMessagesSignal.messagesUpdated(messages);
	}
}

})(window.angular);