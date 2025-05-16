# Bank to Notion Finance OS

## Finance OS


## Set Up

### Notion Finance OS page

### Customize
#### Notion API
Create your **Notion API Key**:
- Go to [Notion Integration](https://www.notion.so/profile/integrations) and log in with your Notion account
- Create a new **Integration** associated to your **workspace** of interest
- Set name to `Finance OS`
- Set to **Internal** type

Once created, copy the **Internal Integration Secret** to [api_token.txt](api_token.txt)

#### Database Integration
On your **Notion Finance OS page**

Now it's time to add all your database ids to the integration.
- Go to your [Finance OS Template/Backend]()
- Open up the [database_ids.csv](database_ids.csv). **For each** of the `database_id`s:
- Navigate to their specific **database** from the **backend**.
- On the top left corner, press the three dots $\cdots$ $\to$ connections $\to$ select `Finance OS` $\to$ Confirm. Now you've added permissions for the **API** to interact with the database
- To obtain the `database_id`, on the **database view**, right left to the **New** button, $\cdots$ $\to$ Copy link to DATABASE_NAME
- You should see something like https://www.notion.so/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...&pvs=... where `XXX...XXX` is a **32 digit number**
- Paste this to the [database_ids.csv](database_ids.csv) on the right row in the following format: `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX` being `8 chars-4 chars-4 chars-4 chars-12 chars`
- **PUT EXTRA ATTENTION IN THIS STEP, SINCE IT'S EXTREMELY EASY TO MESS UP**
- **NOTE**: For the **Months** database, you will notice that there are two entries in the **Backend**. Use the one that has a small arrow on the icon.

Now you should have everything set up propperly, if anything fails in the next steps, make sure you followed every step well.

#### Logic customization
As mentioned above, part of this project's value is the ability to automatically categorize your data. There are two main parts. Determining the type of movement (income, expense or transaction) and then the type of expense based on the concept.

**Type of movement**:
This step highly depends on how your bank exports data, how it formats this outputs and your financial logic. In order to set this with the same logic described earlier:
- Navigate to [csv_processor.py](backend/utils/csv_processor.py)
- In the first lines, modify the `UPPERCASE_VARIABLES` to those suitting your needs.
- Feel free to check the `categorize_transaction` function which applies this logic, and modify it fitting your needs.

**Categorization**:
- Below the variables on the previous step, you will find both `EXPENSE_KEYWORDS` and `INCOME_KEYWORDS` dicts.
- Feel free to add as many filters as you want. These are basic string matching conditions, in the format: `'lowercase_substring':'notion expense type name (case sensitive)'`. For example: `'carrefour'':'Groceries'`

As mentioned, these are very basic logics, but work very effectively, at least in my case. Feel free to modify the code to make room for more advanced categorization techniques (maybe a **ML Approach**?)

### Backend
#### Create venv
Working with `python 3.10.12`
- `cd backend` 
- `python -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

#### Lauch backend
- `cd backend`
- `source venv/bin/activate`
- `uvicorn main:app --host=0.0.0.0 --port=800`
### Frontend


## Run
### Backend
- `uvicorn main:app --host=0.0.0.0 --port=8000`