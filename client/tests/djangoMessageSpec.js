'use strict';

describe('unit tests for module djng-messages', function() {

	beforeEach(function() {
		module('djng-messages');
	});

	describe('django messages signal', function() {

		var signal,
			djngMessagesEvents,
			$rootScope,
			messages = [{title:'title'}];

		beforeEach(inject(function(_$rootScope_, _djngMessagesSignal_, _djngMessagesEvents_) {
			$rootScope = _$rootScope_;
			signal = _djngMessagesSignal_;
			djngMessagesEvents = _djngMessagesEvents_;
		}));

		it('should broadcast a signal when messagesUpdated called', function() {
			spyOn($rootScope, '$broadcast');
			signal.messagesUpdated(messages);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djngMessagesEvents.MESSAGES_UPDATED, messages);
		});

		it('should notify any interested scopes on messages update', function() {
			var scope = $rootScope.$new();
			var result = null;
			var handler = function(msgs) {
				result = msgs;
			}
			signal.onMessagesUpdated(scope, handler);
			signal.messagesUpdated(messages);
			expect(result).toBe(messages);
		});

	});


	describe('django messages interceptor', function() {

		var djngMessagesInterceptor;

		beforeEach(inject(function(_djngMessagesInterceptor_) {
			djngMessagesInterceptor = _djngMessagesInterceptor_;
		}));

		it('should remove django_messages from response data', function() {
			var data = { my_data: 'blah' },
				response = {
					data: {
						data: data,
						django_messages: [{}]
					},
					headers: function() {
						return 'application/json';
					}
				};

			var res = djngMessagesInterceptor.response(response);
			expect(res.data).toBe(data);
		});

		it('should ignore json root object without django_messages property', function() {
			var data = { my_data: 'blah' },
				response = {
					data: data,
					headers: function() {
						return 'application/json';
					}
				};

			var res = djngMessagesInterceptor.response(response);
			expect(res.data).toBe(data);
		});

		it('should ignore json array', function() {
			var data = [],
				response = {
					data: data,
					headers: function() {
						return 'application/json';
					}
				};

			var res = djngMessagesInterceptor.response(response);
			expect(res.data).toBe(data);
		});

		it('should ignore non json content type', function() {
			var data = '<xml></xml>',
				response = {
					data: data,
					headers: function() {
						return 'text/xml';
					}
				};

			var res = djngMessagesInterceptor.response(response);
			expect(res.data).toBe(data);
		});
	});


	describe('django messages interceptor responders', function(){

		var djngMessagesInterceptor,
			response_data,
			messages = [{}],
			response = {
				data: {
					data: {},
					django_messages: messages
				},
				headers: function() {
					return 'application/json';
				}
			},
			responder = {
				addMessages: function(messages) {}
			},
			responder2 = {
				addMessages: function(messages) {}
			};

		beforeEach(inject(function(_djngMessagesInterceptor_) {
			djngMessagesInterceptor = _djngMessagesInterceptor_;
			response_data = angular.extend({}, response); // make copy of response so that original can be re
		}));

		it('should call individual responder with messages', function() {
			spyOn(responder, 'addMessages');
			djngMessagesInterceptor.addResponder(responder);
			djngMessagesInterceptor.response(response_data);
			expect(responder.addMessages).toHaveBeenCalledWith(messages);
		});

		it('should call multiple responders with messages', function() {
			spyOn(responder, 'addMessages');
			spyOn(responder2, 'addMessages');
			djngMessagesInterceptor.addResponder([responder, responder2]);
			djngMessagesInterceptor.response(response_data);
			expect(responder.addMessages).toHaveBeenCalledWith(messages);
			expect(responder2.addMessages).toHaveBeenCalledWith(messages);
		});

		it('should remove specific responder', function() {
			spyOn(responder, 'addMessages');
			spyOn(responder2, 'addMessages');
			djngMessagesInterceptor.addResponder([responder, responder2]);
			djngMessagesInterceptor.response(response_data);
			expect(responder.addMessages).toHaveBeenCalledWith(messages);
			expect(responder2.addMessages).toHaveBeenCalledWith(messages);
			djngMessagesInterceptor.removeResponder(responder);
			response_data = angular.extend({}, response)
			djngMessagesInterceptor.response(response_data);
			expect(responder.addMessages.calls.count()).toBe(1);
			expect(responder2.addMessages.calls.count()).toBe(2);
		});

		iit('should clear all responders', function() {
			spyOn(responder, 'addMessages');
			spyOn(responder2, 'addMessages');
			djngMessagesInterceptor.addResponder([responder, responder2]);
			djngMessagesInterceptor.response(response_data);
			expect(responder.addMessages).toHaveBeenCalledWith(messages);
			expect(responder2.addMessages).toHaveBeenCalledWith(messages);
			djngMessagesInterceptor.clearResponders();
			response_data = angular.extend({}, response)
			djngMessagesInterceptor.response(response_data);
			expect(responder.addMessages.calls.count()).toBe(1);
			expect(responder2.addMessages.calls.count()).toBe(1);
		});
	});


	describe('django messages interceptor and signal integration', function(){

		var signal,
			djngMessagesEvents,
			djngMessagesInterceptor,
			$rootScope,
			messages = [{}],
			response = {
				data: {
					data: {},
					django_messages: messages
				},
				headers: function() {
					return 'application/json';
				}
			};

		beforeEach(inject(function(_$rootScope_, _djngMessagesSignal_, _djngMessagesEvents_, _djngMessagesInterceptor_) {
			$rootScope = _$rootScope_;
			signal = _djngMessagesSignal_;
			djngMessagesEvents = _djngMessagesEvents_;
			djngMessagesInterceptor = _djngMessagesInterceptor_;
		}));

		it('should broadcast an updated event when new messages added', function() {
			spyOn($rootScope, '$broadcast');
			djngMessagesInterceptor.response(response);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djngMessagesEvents.MESSAGES_UPDATED, messages);
		});
	});

});