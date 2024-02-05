package com.apiportal.backend.models;

public class VaultApiInfo {
    private String apiKey;
    private String date;

    public VaultApiInfo() {
    }

    public String getApiKey() {
        return apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    public String getDate() {
        return date;
    }

    public void setDate(String date) {
        this.date = date;
    }
}
