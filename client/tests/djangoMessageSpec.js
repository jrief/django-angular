'use strict';

describe('unit tests for module ng.django.messages', function() {
	
	beforeEach(function() {
		module('ng.django.messages');
	});
	
	describe('django messages signal', function() {
		
		var signal,
			djangoMessagesEvents,
			djangoMessages,
			$rootScope;

		beforeEach(inject(function(_$rootScope_, _djangoMessagesSignal_, _djangoMessagesEvents_, _djangoMessages_) {
			$rootScope = _$rootScope_;
			signal = _djangoMessagesSignal_;
			djangoMessagesEvents = _djangoMessagesEvents_;
			djangoMessages = _djangoMessages_;
		}));

		it('should broadcast a signal when messagesUpdated called', function() {
			spyOn($rootScope, '$broadcast');
			signal.messagesUpdated(djangoMessages);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djangoMessagesEvents.MESSAGES_UPDATED, djangoMessages);
		});

		it('should notify any interested scopes on messages update', function() {
			var scope = $rootScope.$new();
			var model = null;
			var handler = function(mdl) {
				model = mdl;
			}
			signal.onMessagesUpdated(scope, handler);
			signal.messagesUpdated(djangoMessages);
			expect(model).toBe(djangoMessages);
		});
		
		it('should broadcast a signal when messagesCleared called', function() {
			spyOn($rootScope, '$broadcast');
			signal.messagesCleared(djangoMessages);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djangoMessagesEvents.MESSAGES_CLEARED);
		});
		
		it('should notify any interested scopes on messages cleared', function() {
			var scope = $rootScope.$new();
			var called = false;
			var handler = function() {
				called = true;
			}
			signal.onMessagesCleared(scope, handler);
			signal.messagesCleared();
			expect(called).toBe(true);
		});
	
	});
	
	
	describe('django messages interceptor', function() {
		
		var djangoMessagesInterceptor;
		
		beforeEach(inject(function(_djangoMessagesInterceptor_) {
			djangoMessagesInterceptor = _djangoMessagesInterceptor_;
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
			
			var res = djangoMessagesInterceptor.response(response);
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
				
			var res = djangoMessagesInterceptor.response(response);
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
				
			var res = djangoMessagesInterceptor.response(response);
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
				
			var res = djangoMessagesInterceptor.response(response);
			expect(res.data).toBe(data);
		});
	});
	
	
	describe('django messages model', function() {
		
		var djangoMessages;
		
		beforeEach(inject(function(_djangoMessages_) {
			djangoMessages = _djangoMessages_;
		}));
		
		it('should increase count when messages added', function() {
			djangoMessages.addMessages([{message:'one'}]);
			expect(djangoMessages.count).toBe(1);
		});
		
		it('should increase count when new messages added', function() {
			djangoMessages.addMessages([{message:'one'}]);
			expect(djangoMessages.count).toBe(1);
			djangoMessages.addMessages([{message:'two'}]);
			expect(djangoMessages.count).toBe(2);
		});
		
		it('should clear count when messages retrieved', function() {
			djangoMessages.addMessages([{message:'one'}]);
			expect(djangoMessages.count).toBe(1);
			djangoMessages.getMessages();
			expect(djangoMessages.count).toBe(0);
		});
		
		it('should clear count when messages retrieved with true arg', function() {
			djangoMessages.addMessages([{message:'one'}]);
			expect(djangoMessages.count).toBe(1);
			djangoMessages.getMessages(true);
			expect(djangoMessages.count).toBe(0);
		});
		
		it('should not clear count when messages retrieved with false arg', function() {
			djangoMessages.addMessages([{message:'one'}]);
			expect(djangoMessages.count).toBe(1);
			djangoMessages.getMessages(false);
			expect(djangoMessages.count).toBe(1);
		});
		
		it('should allow a single message object to be added', function() {
			djangoMessages.addMessages({message:'one'});
			expect(djangoMessages.count).toBe(1);
		});
		
		it('should allow multiple messages to be added in an array', function() {
			djangoMessages.addMessages([{message:'one'}, {message:'two'}, {message:'three'}]);
			expect(djangoMessages.count).toBe(3);
		});
		
		it('should allow added messages to be retrived', function() {
			var msg = {message:'one'};
			djangoMessages.addMessages([msg]);
			expect(djangoMessages.count).toBe(1);
			var res = djangoMessages.getMessages();
			expect(res[0]).toBe(msg);
			expect(djangoMessages.count).toBe(0);
		});
		
		it('should return multiple messages if they exist', function() {
			var msg_1 = {message:'one'},
				msg_2 = {message:'two'};
				
			djangoMessages.addMessages([msg_1]);
			expect(djangoMessages.count).toBe(1);
			djangoMessages.addMessages([msg_2]);
			expect(djangoMessages.count).toBe(2);
			var res = djangoMessages.getMessages();
			expect(res[0]).toBe(msg_1);
			expect(res[1]).toBe(msg_2);
			expect(djangoMessages.count).toBe(0);
		});
		
		it('should allow messages to be retrieved multiple times when not cleared', function() {
			var msg = {message:'one'};
			djangoMessages.addMessages(msg);
			expect(djangoMessages.count).toBe(1);
			expect(djangoMessages.getMessages(false)[0]).toBe(msg);
			expect(djangoMessages.getMessages(false)[0]).toBe(msg);
			expect(djangoMessages.getMessages(false)[0]).toBe(msg);
			expect(djangoMessages.count).toBe(1);
		});
		
	});
	
	
	describe('django messages model and signal integration', function(){
		
		var signal,
			djangoMessagesEvents,
			djangoMessages,
			$rootScope;

		beforeEach(inject(function(_$rootScope_, _djangoMessagesSignal_, _djangoMessagesEvents_, _djangoMessages_) {
			$rootScope = _$rootScope_;
			signal = _djangoMessagesSignal_;
			djangoMessagesEvents = _djangoMessagesEvents_;
			djangoMessages = _djangoMessages_;
		}));
		
		it('should broadcast an updated event when new messages added', function() {
			spyOn($rootScope, '$broadcast');
			djangoMessages.addMessages([{message:'one'}]);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djangoMessagesEvents.MESSAGES_UPDATED, djangoMessages);
		});
		
		it('should broadcast a cleared event when messages retrieved and cleared', function() {
			spyOn($rootScope, '$broadcast');
			djangoMessages.addMessages([{message:'one'}]);
			djangoMessages.getMessages();
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djangoMessagesEvents.MESSAGES_CLEARED);
			expect(djangoMessages.count).toBe(0);
		});
		
		it('should not broadcast a cleared event if no messages exist', function() {
			spyOn($rootScope, '$broadcast');
			djangoMessages.getMessages();
			expect($rootScope.$broadcast.calls.count()).toBe(0);
		});
		
		it('should not broadcast a cleared event if retrieval arg false', function() {
			spyOn($rootScope, '$broadcast');
			djangoMessages.addMessages([{message:'one'}]);
			djangoMessages.getMessages(false);
			expect($rootScope.$broadcast.calls.count()).toBe(1);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djangoMessagesEvents.MESSAGES_UPDATED, djangoMessages);
		});
	});
	
	
	describe('django messages interceptor and django messages model integration', function() {
		
		var djangoMessagesInterceptor,
			djangoMessages,
			message = {message: 'one'},
			response = {
				data: {
					data: { my_data: 'blah' },
					django_messages: [message]
				},
				headers: function() {
					return 'application/json';
				}
			};
		
		beforeEach(inject(function(_djangoMessagesInterceptor_, _djangoMessages_) {
			djangoMessagesInterceptor = _djangoMessagesInterceptor_;
			djangoMessages = _djangoMessages_;
		}));
		
		it('should add message to django messages model', function() {
			djangoMessagesInterceptor.response(response);
			expect(djangoMessages.count).toBe(1);
			expect(djangoMessages.getMessages()[0]).toBe(message);
		});
		
		it('should not add message to django messages model', function() {
			response.data = {};
			djangoMessagesInterceptor.response(response);
			expect(djangoMessages.count).toBe(0);
		});
	});

});