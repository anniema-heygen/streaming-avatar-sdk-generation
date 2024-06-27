# Streaming Avatar SDK Generation

The Streaming Avatar SDK is generated from `StreamingAvatarSDK.yaml` using the typescript [openapi](https://openapi-generator.tech/docs/generators/typescript-fetch/) generator. However, there is missing polish to this process, as we have to manually supplement some functions to enable easier use for our customers.

This package generates the SDK and provides an interactive interface that fetches these manual changes from the [current SDK](https://github.com/HeyGen-Official/StreamingAvatarSDK) and applies them to the locally generated SDK. It eliminates the need to keep track of the necessary changes in a separate document.

## Usage

To generate a new SDK please do the following:

1. Follow the installation instructions for the openapi generator [here](https://github.com/OpenAPITools/openapi-generator)
2. Install requests module with `pip install requests`
3. Run `python generate.py` and follow the prompts

## How to test

1. `npm link` within the SDK to create a symlink
2. `npm link @heygen/streaming-avatar` where you want to use it to test. Any changes you make within the SDK should automatically appear
3. `npm unlink` to remove the symlink in the end

## How to publish

1. `npm init --scope@heygen` within the SDK, increment the version. Use MIT license.
2. `npm publish --access public`

Alternatively, run `python publish.py`.

## Notes

1. Please do not make changes to the YAML without consulting the team first.
2. For more information on this generation structure please refer to the [openapi documentation](https://swagger.io/specification/).
3. This README is adapted from [this notion page](https://www.notion.so/heygen/Streaming-Avatar-SDK-27fd2ae548d04c8b939f246898e6c344?pvs=4).
