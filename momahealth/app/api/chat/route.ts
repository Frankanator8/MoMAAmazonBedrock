import { bedrock } from "@ai-sdk/amazon-bedrock";
import { convertToModelMessages, streamText, simulateReadableStream } from "ai";

export const maxDuration = 30;

import {
  BedrockAgentRuntimeClient,
  InvokeAgentCommand,
} from "@aws-sdk/client-bedrock-agent-runtime";
import { v4 as uuidv4 } from "uuid";
import { convertOffsetToTimes } from "motion/react";

const client = new BedrockAgentRuntimeClient({
  region: "us-west-2",
  credentials: {
    accessKeyId: "" + process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: "" + process.env.AWS_SECRET_ACCESS_KEY,
  },
});

// @ts-expect-error yea
const extractUrls = (text) => {
  const urlRegex = /(https?:\/\/[^\s]+)/g; // Regex to match URLs
  const matches = text.match(urlRegex);
  return matches ? matches : [];
};

// @ts-expect-error yea
const extractUrlsFromObject = (obj, urls = new Set()) => {
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const value = obj[key];
      if (typeof value === "string") {
// @ts-expect-error yea

        extractUrls(value).forEach((url) => urls.add(url));
      } else if (typeof value === "object" && value !== null) {
        extractUrlsFromObject(value, urls);
      } else if (value instanceof Array) {
        value.forEach((v) => {
          extractUrlsFromObject(v, urls);
        });
      }
    }
  }
  return urls;
};

export async function POST(req: Request) {
  const { messages } = await req.json();

  // const { sessionId } = req.body;
  // if (!sessionId) {
  const sessionId = uuidv4();
  // }

  console.log(messages);
  console.log("=====")
  console.log(convertToModelMessages(messages).map((msg) => msg.content));
  // @ts-expect-error yes
  console.log(convertToModelMessages(messages)[messages.length-1].content[0].text);
  // @ts-expect-error yes
  const inp = convertToModelMessages(messages)[messages.length-1].content[0].text;

  // map((msg) => msg.content));

  const command = new InvokeAgentCommand({
    agentId: "TNM71MN6XL",
        // agentId: process.env.AWS_AGENT_ID,
        // agentAliasId: process.env.AWS_AGENT_ALIAS_ID,
        agentAliasId: "SARJDELTWI",
        inputText: inp + " Assume that all hospitals in the knowledge base are covered.",
        // inputText: convertToModelMessages(messages).map((msg) => msg.content).join("\n"),
        // inputText: convertToModelMessages(messages).map((msg) => msg.content).join("\n"),
        
        sessionId,
      });

      console.log(inp);

  let completion = "";
  const response = await client.send(command);
  
  if (response.completion === undefined) {
      throw new Error("Completion is undefined");
  }
      const set = new Set();
      for await (const chunkEvent of response.completion) {
        const chunk = chunkEvent.chunk;
        const chunkUrls = extractUrlsFromObject(chunk);
        chunkUrls.forEach((url) => set.add(url));
        const decodedResponse = new TextDecoder("utf-8").decode(chunk?.bytes);
        completion += decodedResponse;
      }

      // const urls = [...set];

      // completion = completion.replace(/\n/g, "<br />").replace(": - ", ":<br />- ").replace("<br /><br />", "<br />").trim();

    // return res.status(200).json({ sessionId: sessionId, completion, urls });


  const result = streamText({
    model: bedrock("anthropic.claude-3-5-sonnet-20240620-v1:0"),
    prompt: "Directly return the following string except remove any whitespace and newlines such that the output text is completely inline: " + completion,
    // messages: convertToModelMessages(messages),
  });

// const stream = simulateReadableStream({
//   chunks: ['Hello', ' ', 'World'],
//   initialDelayInMs: 100,
//   chunkDelayInMs: 50,
// });


// TextEncoder objects turn text content
// // into streams of UTF-8 characters.
// // You'll add this encoder to your stream
// const encoder = new TextEncoder();
// // This is the stream object, which clients can read from
// // when you send it as a Function response
// const readableStream = new ReadableStream({
//   // The start method is where you'll add the stream's content
//   start(controller) {
//     const text = 'Stream me!';
//     // Queue the encoded content into the stream
//     controller.enqueue(encoder.encode(text));
//     // Prevent more content from being
//     // added to the stream
//     controller.close();
//   },
// });


// readableStream.pipeThrough(new TextDecoderStream()).getReader();
  console.log(completion);

  // return completion;

  return result.toUIMessageStreamResponse();

  // return new Response(readableStream.pipeThrough(new TextDecoderStream()).getReader(), {
    // headers: { "Content-Type": "text/plain; charset=utf-8" },
  // });
}
