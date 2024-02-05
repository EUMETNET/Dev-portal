package com.apiportal.backend.models;

public class ServerStatus {
    private boolean apisixOnline;
    private boolean apisixUserFound;
    private boolean vaultOnline;
    private boolean vaultUserFound;

    private VaultApiInfo vaultApiInfo;

    public ServerStatus() {
    }

    public boolean isApisixOnline() {
        return apisixOnline;
    }

    public void setApisixOnline(boolean apisixOnline) {
        this.apisixOnline = apisixOnline;
    }

    public boolean isApisixUserFound() {
        return apisixUserFound;
    }

    public void setApisixUserFound(boolean apisixUserFound) {
        this.apisixUserFound = apisixUserFound;
    }

    public boolean isVaultOnline() {
        return vaultOnline;
    }

    public void setVaultOnline(boolean vaultOnline) {
        this.vaultOnline = vaultOnline;
    }

    public boolean isVaultUserFound() {
        return vaultUserFound;
    }

    public void setVaultUserFound(boolean vaultUserFound) {
        this.vaultUserFound = vaultUserFound;
    }

    public VaultApiInfo getVaultApiInfo() {
        return vaultApiInfo;
    }

    public void setVaultApiInfo(VaultApiInfo vaultApiInfo) {
        this.vaultApiInfo = vaultApiInfo;
    }
}
