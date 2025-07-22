package com.streaming.project;

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.errors.StreamsUncaughtExceptionHandler;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Properties;

public class StreamingApplication {

    public static void main(String[] args) {
        Properties appConfig = loadConfiguration();
        Properties streamSettings = createStreamConfig(appConfig);

        // Build topology
        StreamsBuilder builder = new StreamsBuilder();
        StreamReader coinbaseReader = new StreamReader(
                appConfig.getProperty("coinbase.topic.name"),
                appConfig.getProperty("coinbase.source.name"),
                (key, value) -> System.out.println("Key: " + key + ", Value: " + value),
                appConfig.getProperty("schema.registry.url"));
        coinbaseReader.addToBuilder(builder);

        // Create and configure streams
        KafkaStreams streams = new KafkaStreams(builder.build(), streamSettings);
        configureStreamsHandlers(streams);

        System.out.println("Starting streaming application for topic: " + coinbaseReader.getTopicName());

        // Start streams and wait
        streams.start();

        // Graceful shutdown
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));

        try {
            Thread.currentThread().join();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private static Properties loadConfiguration() {
        Properties props = new Properties();
        Path configPath = Paths.get("src/java-streams/main/resources/application.properties");

        try (FileInputStream inputStream = new FileInputStream(configPath.toFile())) {
            props.load(inputStream);
        } catch (IOException e) {
            throw new RuntimeException("Failed to load configuration from: " + configPath, e);
        }
        return props;
    }

    private static Properties createStreamConfig(Properties appConfig) {
        Properties config = new Properties();
        config.put(StreamsConfig.APPLICATION_ID_CONFIG, appConfig.getProperty("kafka.application.id"));
        config.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, appConfig.getProperty("kafka.bootstrap.servers"));
        config.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, appConfig.getProperty("kafka.default.key.serde"));
        config.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, appConfig.getProperty("kafka.default.value.serde"));
        config.put("schema.registry.url", appConfig.getProperty("kafka.schema.registry.url"));
        config.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, appConfig.getProperty("kafka.processing.guarantee"));
        config.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG,
                Integer.parseInt(appConfig.getProperty("kafka.commit.interval.ms")));
        config.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG,
                Integer.parseInt(appConfig.getProperty("kafka.num.stream.threads")));
        return config;
    }

    private static void configureStreamsHandlers(KafkaStreams streams) {
        streams.setStateListener((newState, oldState) -> {
            System.out.println("State changed: " + oldState + " -> " + newState);
            if (newState == KafkaStreams.State.ERROR) {
                System.err.println("Application entered ERROR state!");
            }
        });

        streams.setUncaughtExceptionHandler(exception -> {
            System.err.println("Uncaught exception: " + exception.getMessage());
            exception.printStackTrace();
            return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.SHUTDOWN_APPLICATION;
        });
    }
}
