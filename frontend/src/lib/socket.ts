interface Packet {
  type: "request" | "response" | "exception";
  uid: string;
  data: any;
}

export class Socket {
  buffer_out: Packet[];
  request_callbacks: Map<
    string,
    [(value: unknown) => void, (reason?: any) => void]
  >;
  request_rejects: Map<string, (data: any) => void>;
  callback: (data: any) => Promise<any>;

  constructor(callback: (data: any) => Promise<any>) {
    this.buffer_out = [];
    this.request_callbacks = new Map();
    this.request_rejects = new Map();
    this.callback = callback;
  }

  send(data: any) {
    return new Promise((resolve, reject) => {
      const uid = crypto.randomUUID().toString();
      this.request_callbacks.set(uid, [resolve, reject]);
      this.buffer_out.push({ type: "request", uid, data });
    });
  }

  communicate(packets: Packet[]) {
    for (const { type, uid, data } of packets) {
      if (type === "response") {
        const callbacks = this.request_callbacks.get(uid);
        if (callbacks === undefined) continue;
        this.request_callbacks.delete(uid);
        callbacks[0](data);
      } else if (type === "exception") {
        const callbacks = this.request_callbacks.get(uid);
        if (callbacks === undefined) continue;
        this.request_callbacks.delete(uid);
        callbacks[1](data);
      } else if (type === "request") {
        this.callback(data).then(
          (data) => this.buffer_out.push({ type: "response", uid, data }),
          (exception) =>
            this.buffer_out.push({
              type: "exception",
              uid,
              data: exception.toString(),
            }),
        );
      }
    }
    const buffer = this.buffer_out;
    this.buffer_out = [];
    return buffer;
  }
}
