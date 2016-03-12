#define AsynchronousTask

class AsynchronousTask {
	public:
		bool refresh();
	protected:
		virtual bool initialize() = 0;
		virtual bool workToCompletion() = 0;
		const enum Status { INIT, WORK, DONE };
		Status status;
}

bool AsynchronousTask::refresh() {
	switch (status) {
		case INIT:
			if( initialize() ) {
				status = WORK;
			}
			break;
		case WORK:
			if( workToCompletion() ) {
				status = DONE;
			}
			break;
		case DONE:
			//no action
			break;
	}
	return status == DONE;
}
