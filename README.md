# serverless-inventory-tracker

# Serverless Inventory Tracking System on AWS

This project demonstrates how to implement a **serverless architecture** on AWS for inventory tracking.  
It uses **Amazon S3, Lambda, DynamoDB, and SNS** to process inventory files, store data, and send notifications when stock runs out.

<img width="2052" height="940" alt="image" src="https://github.com/user-attachments/assets/622a8cc3-de37-422c-a659-746dc654c50e" />

---

## 🏗 Architecture Overview

1. **S3 Upload**  
   - Stores upload inventory `.csv` files to an Amazon S3 bucket.  

2. **Lambda - Load Inventory**  
   - Triggered by an S3 upload event.  
   - Reads the file, parses the rows, and loads inventory data into a DynamoDB table.  

3. **DynamoDB (Inventory Table)**  
   - Stores inventory data with attributes:  
     - `Store` (Partition Key)  
     - `Item` (Sort Key)  
     - `Count` (Number)  

4. **Lambda - Check Stock**  
   - Triggered by DynamoDB Streams whenever new data is inserted.  
   - Checks inventory levels and sends a notification if any item is out of stock.  

5. **SNS Notifications**  
   - Sends alerts by email or SMS to subscribed recipients.  

6. **Dashboard (Optional)**  
   - A static S3-hosted web app that authenticates via Amazon Cognito.  
   - Displays inventory levels by retrieving data directly from DynamoDB.  

---


---

## 🚀 Step-by-Step Instructions

Follow these steps to deploy the system in your AWS account.

---

### 1. Clone the Repository
```bash
git clone https://github.com/salahali20/serverless-inventory-tracker.git
cd serverless-inventory-tracker
## Deployment Steps

### 2. Create an S3 Bucket
1. Go to **AWS Management Console → S3 → Create bucket**.  
2. Enter a unique bucket name, e.g., `inventory-12345`.  
3. Leave all defaults and click **Create bucket**.  

---

### 3. Create DynamoDB Table
1. Go to **AWS Console → DynamoDB → Create table**.  
2. Configure the table:  
   - **Table name:** `Inventory`  
   - **Partition key:** `Store` (String)  
   - **Sort key:** `Item` (String)  
3. Leave other options as default → **Create table**.  

---

### 4. Create Load-Inventory Lambda
1. Go to **AWS Console → Lambda → Create function**.  
2. Configure:  
   - **Function name:** `Load-Inventory`  
   - **Runtime:** Python 3.8+  
   - **Execution role:** select or create `Lambda-Load-Inventory-Role`  
     - Must have: `AmazonS3ReadOnlyAccess` + `AmazonDynamoDBFullAccess`  
3. After creation, open the function → **Code tab**.  
4. Replace the code with:  
   - `lambdas/load_inventory/lambda_function.py`  
5. Click **Deploy**.  

---

### 5. Configure S3 Trigger for Load-Inventory
1. Go to your **S3 bucket**.  
2. Open **Properties → Event notifications → Create event notification**.  
3. Configure:  
   - **Event name:** `Load-Inventory-Event`  
   - **Event types:** All object create events  
   - **Destination:** Lambda function → `Load-Inventory`  
4. Save changes.  

✅ Now whenever a file is uploaded to S3, the Lambda will process it and insert data into DynamoDB.  

---

### 6. Create SNS Topic
1. Go to **AWS Console → SNS → Create topic**.  
2. Configure:  
   - **Name:** `NoStock`  
   - **Type:** Standard  
3. On the topic page, create a **Subscription**:  
   - **Protocol:** Email (or SMS)  
   - **Endpoint:** enter your email/phone number  
4. Confirm the subscription from your inbox or SMS.  

---

### 7. Create Check-Stock Lambda
1. Go to **AWS Console → Lambda → Create function**.  
2. Configure:  
   - **Function name:** `Check-Stock`  
   - **Runtime:** Python 3.8+  
   - **Execution role:** `Lambda-Check-Stock-Role`  
     - Must have: `AmazonDynamoDBReadOnlyAccess` + `AmazonSNSFullAccess`  
3. Replace the code with:  
   - `lambdas/check_stock/lambda_function.py`  
4. Click **Deploy**.  

---

### 8. Configure DynamoDB Stream Trigger for Check-Stock
1. Go to your **Inventory table → Exports and streams**.  
2. Enable **DynamoDB Streams** with `New image`.  
3. Return to your `Check-Stock` Lambda.  
4. In **Configuration → Triggers → Add trigger**:  
   - **Source:** DynamoDB  
   - **Table:** Inventory  
   - **Stream:** latest one  
   - **Batch size:** leave default  
5. Save changes.  

Now, whenever a new record is inserted into DynamoDB, the `Check-Stock` Lambda will check for out-of-stock items and send an SNS notification.  

---

### 9. Test the System
1. Upload a file from `sample-data/` to your S3 bucket.  
   - Example: `inventory-berlin.csv`  
2. Check:  
   - **DynamoDB → Inventory table → Explore table items** → verify rows are inserted  
   - If any item has `Count = 0`, you should receive an email/SMS alert  
3. Try uploading multiple files (e.g., `inventory-calcutta.csv`) to test scale and multiple store data.  

---

## Example Inventory File

```csv
store,item,count
Berlin,Echo Dot,12
Berlin,Echo (2nd Gen),19
Berlin,Echo Show,18
Berlin,Echo Plus,0
Berlin,Echo Look,10
Berlin,Amazon Tap,15





