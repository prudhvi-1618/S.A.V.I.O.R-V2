import { fetchEventSource } from '@microsoft/fetch-event-source';

export class SSEClient {
  private abortController: AbortController | null = null;

  connect(
    url: string,
    onEvent: (event: string, data: any) => void,
    onError: (error: any) => void,
    onComplete: () => void
  ) {
    this.abortController = new AbortController();

    fetchEventSource(url, {
      method: 'POST',
      headers: {
        'Accept': 'text/event-stream',
      },
      signal: this.abortController.signal,
      onmessage: (msg) => {
        try {
          const data = JSON.parse(msg.data);
          onEvent(msg.event, data);
          if (msg.event === 'processing_complete' || msg.event === 'processing_error') {
            this.disconnect();
            onComplete();
          }
        } catch (e) {
          console.error("Failed to parse SSE message", e);
        }
      },
      onerror: (err) => {
        onError(err);
        this.disconnect();
        throw err; // Stop retrying
      },
      onclose: () => {
        onComplete();
      }
    });
  }

  disconnect() {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }
}
