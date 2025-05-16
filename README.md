# CaixaEnginyers2NotionBudget


## Set Up

### Notion Finance OS page

### Customize
#### Notion API
Create your **Notion API Key**:
- Go to [Notion Integration](https://www.notion.so/profile/integrations)
- Create a new **Integration** associated to your **workspace** of interest
- Set to **Internal** type

Once created, copy the **Internal Integration Secret** to [api_token.txt](api_token.txt)

#### Database Integration
On your **Notion Finance OS page**


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