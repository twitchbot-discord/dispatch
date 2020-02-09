# Dispatch

Dispatch is a web dashboard and protocol that processes and saves AMQP events, most likely used for logging.

> Note: Dispatch is heavily a work-in-progress.

## Requirements
 - Python 3.8
 - All pip packages in *requirements.txt*
 - An AMQP server (RabbitMQ is most recommended)
 - A RethinkDB instance with the following:
   - A database called `dispatch`
   - `logs` and `users` tables

## How does it work?

Dispatch takes messages from the `dispatch.logs` queue (on the default channel) and writes them to RethinkDB. Logs can be viewed at any time from the convenient web dashboard.

## Dispatch protocol

All events are sent through the AMQP server are JSON-encoded.
Here's what an example dispatch log event looks like:
```js
{
  "op": 1, // The opcode for logging events
  "level": 0, // Log levels 0-3 are valid. They correspond to: debug, info, warning, error
  "channel": "example-channel", // Acts as a service group
  "source": "example-source", // Acts as a subset of channel
  "ts": 1581280736.3617833, // Unix timestamp of when the event occurred
  "msg": "Some log content here",
  "data": { // An object of other metadata associated with the event
    "key": "value"
  }
}
```

### About the `source` property

The source property acts as a subset of a channel. Its main intention is to provide a unique identifier to each separate process that sends events to Dispatch.

For example: if you have multiple workers for a single service, you might communicate worker events through the same channel, and give each worker a different source.

#### Example logging events
| Worker 1 | Worker 2 |
| -------- | -------- |
| `{channel: 'myChannel', source: 'worker1', ...}` | `{channel: 'myChannel', source: 'worker2', ...}` |

## Client libraries

There are currently no official client libraries for Dispatch. However, libraries for Java, Python, and TypeScript are planned. You can easily write your own Dispatch library in any language that has an AMQP client library.
