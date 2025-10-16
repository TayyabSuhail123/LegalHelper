# HealthApi

All URIs are relative to _http://localhost_

| Method                                                                                      | HTTP request                    | Description           |
| ------------------------------------------------------------------------------------------- | ------------------------------- | --------------------- |
| [**detailedHealthCheckApiV1HealthDetailedGet**](#detailedhealthcheckapiv1healthdetailedget) | **GET** /api/v1/health/detailed | Detailed Health Check |
| [**healthCheckApiV1HealthGet**](#healthcheckapiv1healthget)                                 | **GET** /api/v1/health          | Health Check          |

# **detailedHealthCheckApiV1HealthDetailedGet**

> any detailedHealthCheckApiV1HealthDetailedGet()

Detailed health check endpoint. Returns: dict: Detailed system health information

### Example

```typescript
import { HealthApi, Configuration } from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } =
  await apiInstance.detailedHealthCheckApiV1HealthDetailedGet();
```

### Parameters

This endpoint does not have any parameters.

### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **healthCheckApiV1HealthGet**

> HealthResponse healthCheckApiV1HealthGet()

Health check endpoint. Returns: HealthResponse: Current application health status

### Example

```typescript
import { HealthApi, Configuration } from './api';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthCheckApiV1HealthGet();
```

### Parameters

This endpoint does not have any parameters.

### Return type

**HealthResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details

| Status code | Description         | Response headers |
| ----------- | ------------------- | ---------------- |
| **200**     | Successful Response | -                |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
