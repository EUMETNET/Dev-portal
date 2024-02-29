
package com.apiportal.backend.apisix.models.Route;

import java.util.LinkedHashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;

@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonPropertyOrder({
    "plugins",
    "upstream",
    "status",
    "uri",
    "id",
    "priority",
    "update_time",
    "create_time"
})
@Generated("jsonschema2pojo")
public class Value {

    @JsonProperty("plugins")
    private Plugins plugins;
    @JsonProperty("upstream")
    private Upstream upstream;
    @JsonProperty("status")
    private Integer status;
    @JsonProperty("uri")
    private String uri;
    @JsonProperty("id")
    private String id;
    @JsonProperty("priority")
    private Integer priority;
    @JsonProperty("update_time")
    private Integer updateTime;
    @JsonProperty("create_time")
    private Integer createTime;
    @JsonIgnore
    private Map<String, Object> additionalProperties = new LinkedHashMap<String, Object>();

    @JsonProperty("plugins")
    public Plugins getPlugins() {
        return plugins;
    }

    @JsonProperty("plugins")
    public void setPlugins(Plugins plugins) {
        this.plugins = plugins;
    }

    @JsonProperty("upstream")
    public Upstream getUpstream() {
        return upstream;
    }

    @JsonProperty("upstream")
    public void setUpstream(Upstream upstream) {
        this.upstream = upstream;
    }

    @JsonProperty("status")
    public Integer getStatus() {
        return status;
    }

    @JsonProperty("status")
    public void setStatus(Integer status) {
        this.status = status;
    }

    @JsonProperty("uri")
    public String getUri() {
        return uri;
    }

    @JsonProperty("uri")
    public void setUri(String uri) {
        this.uri = uri;
    }

    @JsonProperty("id")
    public String getId() {
        return id;
    }

    @JsonProperty("id")
    public void setId(String id) {
        this.id = id;
    }

    @JsonProperty("priority")
    public Integer getPriority() {
        return priority;
    }

    @JsonProperty("priority")
    public void setPriority(Integer priority) {
        this.priority = priority;
    }

    @JsonProperty("update_time")
    public Integer getUpdateTime() {
        return updateTime;
    }

    @JsonProperty("update_time")
    public void setUpdateTime(Integer updateTime) {
        this.updateTime = updateTime;
    }

    @JsonProperty("create_time")
    public Integer getCreateTime() {
        return createTime;
    }

    @JsonProperty("create_time")
    public void setCreateTime(Integer createTime) {
        this.createTime = createTime;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperty(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

}
