# Exercise 2: Extracting Complex Structured Data with a Lease Abstract
One of the most common questions we get at Beehive Advisors: how do we accurately extract structured data from documents? 

First, you need to point the AI to the document. Second, you must define three things in your prompt: 
1) The data's name
2) A description of the data and where to find it in the document
3) The data output format (aka, the data "type")

The best way to organize this is in a table. Let's say we wanted to extract the tenant:
| Field | Description | Type |
|---|---|---|
| tenant | Name of the tenant's organization  | string |

## Exercise 2.1: creating a data "schema" 
A schema is the formal definition of how data is structured. Let's define the data we wish to extract using [blank-schema.xlsx](./schema.xlsx).

Open the Excel file and fill in the field definitions and types. All the cells you need to populate are highlighted in green. 

## Exercise 2.2: upload the lease & schema to cowork and execute your first abstract
Upload the [Ironhide_Cold_Logistics_Industrial_Lease.pdf](Ironhide lease) to Cowork and paste in your schema. Create a prompt that asks Copilot to abstract the Ironhide lease using the schema you provided. Ask Claude to return its answer in a table. 

## Exercise 2.3: write your data to our Excel "database" 
First, inspect the file named [database.xlsx](./database.xlsx). The Excel worksheet is our fictional database, and the tabs represent the different tables within the database. 

Ask Claude to write the abstracted lease to our Excel database. 

## Exercise 2.4: create an agent skill
Agent skills are just text files that describe a action or set of actions you wish to execute at once.

No sense in explaining more - let's make one together. Ask Claude to use your conversation history & to ask any outstanding questions to you, the user. 

## Exercise 2.5: Save the agent skill to Claude Cowork
Once you've reviewed the agent skill, explicitly ask Claude to add the agent skill to Cowork. This allows you evoke the agent skill using slash (`/`) notation within the Claude interface. 

We'll use `/` noation in our next exercise (`3-automation-with-agent-skills`).