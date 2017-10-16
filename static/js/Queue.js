//code.stephenmorley.org
function Queue(){
	storage = {};
	length = 0;
	
	this.getLength = function(){
		return length;
	}

	this.push = function(a,b){
		storage[a] = b;
		length += 1;
	};

	this.pop = function(b){
		if (length == 0) { return ;}
		if (storage[b] != undefined){
			length -= 1;
			value = storage[b];
			delete storage[b];
			return value;
		}
	};

	this.print = function(){
		return storage;
	}
};

