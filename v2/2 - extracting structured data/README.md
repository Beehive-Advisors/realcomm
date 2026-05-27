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

## Exercise 2.1: 


For simplicity's sake, we'll use [.xlsx](./blank-schema.xlsx)