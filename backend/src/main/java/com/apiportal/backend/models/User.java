package com.apiportal.backend.models;

import java.util.List;

public class User {
    private String userName;
    private String apiKey;

    private List<String> routes;

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public String getApiKey() {
        return apiKey;
    }

    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }

    public List<String> getRoutes() {return routes;}

    public void setRoutes(List<String> routes) {this.routes = routes;}
}
