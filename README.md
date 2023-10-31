# How to Deploy

Follow these steps to deploy your project using the Serverless Framework and AWS:

## Step 1: Create AWS IAM Access Key

1. Log in to your AWS (Amazon Web Services) Console.
2. Navigate to the Identity and Access Management (IAM) service.
3. In the IAM dashboard, select "Users" on the left sidebar.
4. Choose the user for which you want to create an Access Key or create a new user.
5. Under the "Security credentials" tab, find the "Access keys" section and click "Create access key."
6. Note down the Access Key ID and Secret Access Key that are generated. You will need these for configuration.

## Step 2: Configure AWS Credentials

Open your command-line terminal and run the following command, replacing `<ACCESS KEY>` and `<SECRET>` with the Access Key ID and Secret Access Key you obtained in Step 1:

```bash
serverless config credentials --provider aws --key <ACCESS KEY> --secret <SECRET>
```

## Step 3:  Deploy

```bash
serverless deploy
```
