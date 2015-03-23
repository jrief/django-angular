'use strict';

describe('unit tests for module ng.django.messages', function() {
	
	beforeEach(function() {
		module('ng.django.messages');
	});
	
	describe('django messages signal', function() {
		
		var signal,
			djngMessagesEvents,
			djngMessagesModel,
			$rootScope;

		beforeEach(inject(function(_$rootScope_, _djngMessagesSignal_, _djngMessagesEvents_, _djngMessagesModel_) {
			$rootScope = _$rootScope_;
			signal = _djngMessagesSignal_;
			djngMessagesEvents = _djngMessagesEvents_;
			djngMessagesModel = _djngMessagesModel_;
		}));

		it('should broadcast a signal when messagesUpdated called', function() {
			spyOn($rootScope, '$broadcast');
			signal.messagesUpdated(djngMessagesModel);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djngMessagesEvents.MESSAGES_UPDATED, djngMessagesModel);
		});

		it('should notify any interested scopes on messages update', function() {
			var scope = $rootScope.$new();
			var model = null;
			var handler = function(mdl) {
				model = mdl;
			}
			signal.onMessagesUpdated(scope, handler);
			signal.messagesUpdated(djngMessagesModel);
			expect(model).toBe(djngMessagesModel);
		});
		
		it('should broadcast a signal when messagesCleared called', function() {
			spyOn($rootScope, '$broadcast');
			signal.messagesCleared(djngMessagesModel);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djngMessagesEvents.MESSAGES_CLEARED);
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
	
	
	describe('django messages model', function() {
		
		var djngMessagesModel;
		
		beforeEach(inject(function(_djngMessagesModel_) {
			djngMessagesModel = _djngMessagesModel_;
		}));
		
		it('should increase count when messages added', function() {
			djngMessagesModel.addMessages([{message:'one'}]);
			expect(djngMessagesModel.count).toBe(1);
		});
		
		it('should increase count when new messages added', function() {
			djngMessagesModel.addMessages([{message:'one'}]);
			expect(djngMessagesModel.count).toBe(1);
			djngMessagesModel.addMessages([{message:'two'}]);
			expect(djngMessagesModel.count).toBe(2);
		});
		
		it('should clear count when messages retrieved', function() {
			djngMessagesModel.addMessages([{message:'one'}]);
			expect(djngMessagesModel.count).toBe(1);
			djngMessagesModel.getMessages();
			expect(djngMessagesModel.count).toBe(0);
		});
		
		it('should clear count when messages retrieved with true arg', function() {
			djngMessagesModel.addMessages([{message:'one'}]);
			expect(djngMessagesModel.count).toBe(1);
			djngMessagesModel.getMessages(true);
			expect(djngMessagesModel.count).toBe(0);
		});
		
		it('should not clear count when messages retrieved with false arg', function() {
			djngMessagesModel.addMessages([{message:'one'}]);
			expect(djngMessagesModel.count).toBe(1);
			djngMessagesModel.getMessages(false);
			expect(djngMessagesModel.count).toBe(1);
		});
		
		it('should allow a single message object to be added', function() {
			djngMessagesModel.addMessages({message:'one'});
			expect(djngMessagesModel.count).toBe(1);
		});
		
		it('should allow multiple messages to be added in an array', function() {
			djngMessagesModel.addMessages([{message:'one'}, {message:'two'}, {message:'three'}]);
			expect(djngMessagesModel.count).toBe(3);
		});
		
		it('should allow added messages to be retrived', function() {
			var msg = {message:'one'};
			djngMessagesModel.addMessages([msg]);
			expect(djngMessagesModel.count).toBe(1);
			var res = djngMessagesModel.getMessages();
			expect(res[0]).toBe(msg);
			expect(djngMessagesModel.count).toBe(0);
		});
		
		it('should return multiple messages if they exist', function() {
			var msg_1 = {message:'one'},
				msg_2 = {message:'two'};
				
			djngMessagesModel.addMessages([msg_1]);
			expect(djngMessagesModel.count).toBe(1);
			djngMessagesModel.addMessages([msg_2]);
			expect(djngMessagesModel.count).toBe(2);
			var res = djngMessagesModel.getMessages();
			expect(res[0]).toBe(msg_1);
			expect(res[1]).toBe(msg_2);
			expect(djngMessagesModel.count).toBe(0);
		});
		
		it('should allow messages to be retrieved multiple times when not cleared', function() {
			var msg = {message:'one'};
			djngMessagesModel.addMessages(msg);
			expect(djngMessagesModel.count).toBe(1);
			expect(djngMessagesModel.getMessages(false)[0]).toBe(msg);
			expect(djngMessagesModel.getMessages(false)[0]).toBe(msg);
			expect(djngMessagesModel.getMessages(false)[0]).toBe(msg);
			expect(djngMessagesModel.count).toBe(1);
		});
		
	});
	
	
	describe('django messages model and signal integration', function(){
		
		var signal,
			djngMessagesEvents,
			djngMessagesModel,
			$rootScope;

		beforeEach(inject(function(_$rootScope_, _djngMessagesSignal_, _djngMessagesEvents_, _djngMessagesModel_) {
			$rootScope = _$rootScope_;
			signal = _djngMessagesSignal_;
			djngMessagesEvents = _djngMessagesEvents_;
			djngMessagesModel = _djngMessagesModel_;
		}));
		
		it('should broadcast an updated event when new messages added', function() {
			spyOn($rootScope, '$broadcast');
			djngMessagesModel.addMessages([{message:'one'}]);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djngMessagesEvents.MESSAGES_UPDATED, djngMessagesModel);
		});
		
		it('should broadcast a cleared event when messages retrieved and cleared', function() {
			spyOn($rootScope, '$broadcast');
			djngMessagesModel.addMessages([{message:'one'}]);
			djngMessagesModel.getMessages();
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djngMessagesEvents.MESSAGES_CLEARED);
			expect(djngMessagesModel.count).toBe(0);
		});
		
		it('should not broadcast a cleared event if no messages exist', function() {
			spyOn($rootScope, '$broadcast');
			djngMessagesModel.getMessages();
			expect($rootScope.$broadcast.calls.count()).toBe(0);
		});
		
		it('should not broadcast a cleared event if retrieval arg false', function() {
			spyOn($rootScope, '$broadcast');
			djngMessagesModel.addMessages([{message:'one'}]);
			djngMessagesModel.getMessages(false);
			expect($rootScope.$broadcast.calls.count()).toBe(1);
			expect($rootScope.$broadcast).toHaveBeenCalledWith(djngMessagesEvents.MESSAGES_UPDATED, djngMessagesModel);
		});
	});
	
	
	describe('django messages interceptor and django messages model integration', function() {
		
		var djngMessagesInterceptor,
			djngMessagesModel,
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
		
		beforeEach(inject(function(_djngMessagesInterceptor_, _djngMessagesModel_) {
			djngMessagesInterceptor = _djngMessagesInterceptor_;
			djngMessagesModel = _djngMessagesModel_;
		}));
		
		it('should add message to django messages model', function() {
			djngMessagesInterceptor.response(response);
			expect(djngMessagesModel.count).toBe(1);
			expect(djngMessagesModel.getMessages()[0]).toBe(message);
		});
		
		it('should not add message to django messages model', function() {
			response.data = {};
			djngMessagesInterceptor.response(response);
			expect(djngMessagesModel.count).toBe(0);
		});
	});

});