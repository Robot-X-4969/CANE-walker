#define BufferedArray_h

class BufferedArray
{
	public:
		void construct(int size);
		int getSize();
		void push(double val);
		double get(int index);
		double median();
		double mean();
		BufferedArray getSortedBuffer();
		BufferedArray getTrimmedBuffer(int nErasures); //erase from both ends
	private:
		double *buffAddr;
		int size;
		void set(int index, double val);
};

BufferedArray::construct(int bufferSize) {
	double temp[bufferSize];
	buffAddr = temp;
	size = bufferSize;
}

int BufferedArray::getSize() {
	return size;
}

void BufferedArray::push(double val) {
	for(int i = 1; i < size; i++) {
		set( i-1, get(i) );
	}
	set(size, val);
}

void BufferedArray::set(int index, double val) {
	*(buffAddr+index) = val;
}

double BufferedArray::get(int index) {
	return *(buffAddr+index);
}

double BufferedArray::mean() {
	double total = 0.0;
	for(int i = 0; i < size; i++) {
		total += get(i);
	}
	return (total / (double)size);
}

BufferedArray BufferedArray::getSortedBuffer() {
	BufferedArray out(size);
	for(int pass = 0; pass < (size-1); pass++){
		int min_id = pass;
		for(int i = pass; i < size; i++) {
			if(get(i) < get(min_id)) {
				min_id = i;
			}
		}
		double temp = get(pass);
		set(pass, get(min_id));
		set(min_id, temp);
	}
	return out;
}

BufferedArray BufferedArray::getTrimmedBuffer(int nErasures) {
	BufferedArray out(size-nErasures*2);
	for(int i = nErasures; i < size-nErasures; i++) {
		out.push( get(i) );
	}
	return out;
}

double BufferedArray::median() {
	//size 1 or 2 removes no elements from each side, 3-4 removes 1, 5-6 removes 2, etc
	int nErasures = ( (size%2 == 0) ? size-2 : size-1 ) / 2;
	return getSortedBuffer().getTrimmedBuffer(nErasures).mean();
}

