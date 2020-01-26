# API-DOC-2

### Docker Setup

PLS mount the conf file into /api/conf.yaml

### Installation

```sh
$ pip install -r requirements.txt
$ ./build_modules.sh
```


## Summary

Better

---

Grills and bois it has finally arrived 
We have the new version of api-doc

WHY ? :
* Harder
* Faster
* Stronger

For real tho:

* Will be able to make <span style="color:orange;">**TABLES**</span> !!
* Now support types WHICH MEANS that we'll soon be able to make <span style="color:orange;">REM's</span> and <span style="color:orange;">CET's</span>


## How to transition ?

### Change the POST request

Example

```python
 {
    'data':  {
        'mission': {
            'contact': {
                'civility': {
                    'value': 'JEB'
                }
            }
        },
        'student':{
            'name':{
                'value':'Paul'
            }
        }
    },
    'template_name': 'DDE',
    'filename': 'test.docx',
    'type': 'mission'
}
```
#### `data` 

data is like previous data but with types now

* to render `mission.contact.civility.value` you have to put it under the `mission.contact.civility.value` key

Which means that now you can just deserialize the data from the db to that api

You can now render :

`student.name.value`

`mission.name.value`

without breaking a sweat

Just think about bringing the easyness to a new level !

#### `template_name`

Self explenatory ?

#### `type` 

We will have multiple document repositories from now on, ex: (tresorerie, ...etc)

#### `filename` 

That's the desired filename save, that's the previous `generated_name`

## Add the reload button in the Parameters directory

To have a faster response time and avoid re-parsing the documents all day- everyday we now cache the results `;)`

Das some phoenix-front + phoenix-back stuff




## `manifest`

That's a config telling the app where to find repositories
It's supposed to be stored inside the conf file


## Check the test files for more information !


## TODO 

- Add syntax for auto-table detection -> should be handled by make model -> YAS

You have to specify the loop variable name to have model_auto_creation :