## JSON Field contains (@>) array of jsons

### DB object

```json
{
  "patient_details1": "1",
  "patient_details2": "2021-10-04",
  "patient_details3": "Male",
  "patient_details4": 182,
  "patient_details5": 90,
  "patient_details6": 39,
  "patient_details7": "White",
  "patient_details8": "Widowed",
  "patient_details9": "SEng",
  "patient_details10": [
    {
      "Column 1": "test"
    },
    {
      "Column 1": "test2"
    }
  ],
  "patient_details14": "diagnosis1"
}
```

### Filter object

```json
{
  "filter": [
    {
      "json_field": "demographics",
      "node": "patient_details10",
      "operator": "@>",
      "valueType": "jsonb",
      "values": "[{\"Column 1\":\"test\"}]"
    }
  ]
}
```