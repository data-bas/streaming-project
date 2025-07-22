package com.streaming.project;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.ForeachAction;
import io.confluent.kafka.streams.serdes.avro.GenericAvroSerde;
import org.apache.avro.generic.GenericRecord;

import java.util.Collections;

public class StreamReader {
    private final String topicName;
    private final String streamName;
    private final ForeachAction<String, GenericRecord> processor;
    private final GenericAvroSerde genericAvroSerde;

    public StreamReader(String topicName, String streamName, ForeachAction<String, GenericRecord> processor,
            String schemaRegistryUrl) {
        this.topicName = topicName;
        this.streamName = streamName;
        this.processor = processor;

        // Configure Avro serde for values
        this.genericAvroSerde = new GenericAvroSerde();
        this.genericAvroSerde.configure(
                Collections.singletonMap("schema.registry.url", schemaRegistryUrl),
                false); // false for value serializer
    }

    public void addToBuilder(StreamsBuilder builder) {
        KStream<String, GenericRecord> stream = builder.stream(topicName,
                Consumed.with(Serdes.String(), genericAvroSerde));

        stream.peek(processor);
    }

    public String getTopicName() {
        return topicName;
    }

    public String getStreamName() {
        return streamName;
    }
}
