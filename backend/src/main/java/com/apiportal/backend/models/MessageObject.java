package com.apiportal.backend.models;

public class MessageObject {
    private String message;

    public MessageObject(String message) {
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}