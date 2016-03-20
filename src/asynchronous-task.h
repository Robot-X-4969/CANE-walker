#define AsynchronousTask_h

enum Status { INIT, WORK, DONE };

class AsynchronousTask
{
	public:
		AsynchronousTask();
		bool refresh();
		void reset();
	protected:
		virtual bool initialize() { return true; }
		virtual bool workToCompletion() { return true; }
		Status status;
};

AsynchronousTask::AsynchronousTask() {
	reset();
}

void AsynchronousTask::reset() {
	status = INIT;
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
