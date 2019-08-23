# API-DOC-2

## Summary

Better but /!\ doesn't support **Shapes** /!\ 

---

Grills and bois it has finally arrived 
We have the new version of api-doc

WHY ? :
* Harder
* Faster
* Stronger

For real tho:

* Not relying on strange libraries for templating -> can template the fuck out anything
* Will be able to make <span style="color:orange;">**TABLES**</span> !!
* Now support types WICH MEANS that we'll soon be able to make <span style="color:orange;">REM's</span> and <span style="color:orange;">CET's</span>


## How to transition ?

### Change the POST request

Example

```python
 {
    'data': json.dumps({
        'mission': {
            'projectManager_student_firstName': 'Jack'
        },
        'student':{
            'name_value':'Paul'
        }}),
    'template_name': 'DDE',
    'filename': 'test.docx',
    'type': 'mission'
}
```
#### `data` 

data is like previous data but with types now

* to render `mission::projectManager_student_firstName` you have to put it under the `mission` key
* to render `student::name_value` you have ti put it under the `student` key

You can now render :

`student::name_value`

`mission::name_value`

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




## `manifest.json`

That's a config file telling the app where to find repositories
It's supposed to be stored on minio too

## Check the test files for more information !