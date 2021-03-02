openapi: 3.0.1
info:
  title: DSR API
  description: ""
  license:
    name: Apache 2.0
    url: http://www.apache.org/licenses/LICENSE-2.0.html
  version: 0.1.0
servers:
- url: http://localhost:8000/
tags:
- name: dsrs
  description: DSR API
- name: resources
  description: DSR Resources API
paths:
  /dsrs/:
    get:
      tags:
      - dsrs
      responses:
        200:
          description: An array of DSR in JSON format.
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/DSR'

  /dsrs/{id}:
    get:
      tags:
      - dsrs
      summary: Get dsr details
      parameters:
      - name: id
        in: path
        required: true
        schema:
          type: integer
      responses:
        200:
          description: DSR found in JSON format.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DSR'
        404:
          description: DSR does not exist.
          content:
            application/json:
              schema:
                type: object
                properties:
                  detail:
                    type: string
                    default: Not found.

  /resources/percentile/{number}:
    get:
      tags:
      - resources
      summary: TOP percentile by revenue.
      description: This resource returns the TOP percentile by revenue (inverse of percentile). For example, "top percentile 10" returns the unique resources by revenue that accounts 10% of the total revenue.
      parameters:
      - name: number
        in: path
        required: true
        description: Number.
        schema:
          type: integer
          minimum: 1
          maximum: 100
      - name: territory
        in: query
        schema:
          type: string
        description: Territory code. ES, FR..
      - name: period_start
        in: query
        schema:
          type: string
          format: date-time
        description: Datetime of the starting date of the associated DSRs
      - name: period_end
        in: query
        schema:
          type: string
          format: date-time
        description: Datetime of the ending date of the associated DSRs.
      responses:
        200:
          description: List of resources in JSON format ordered by revenue in EURO
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Resource'

components:
  schemas:
    DSR:
      type: object
      required:
        - id
        - path
        - period_start
        - period_end
        - status
        - territory
        - currency
      properties:
        id:
          type: integer
        path:
          type: string
          default: '/path/to/dsr.csv'
        period_start:
          type: string
          format: date-time
        period_end:
          type: string
          format: date-time
        status:
          type: string
          enum: ['failed', 'ingested']
          default: 'ingested'
        territory:
          type: object
          properties:
            name:
              type: string
              default: Spain
            code_2:
              type: string
              default: ES
        currency:
          type: object
          properties:
            name:
              type: string
              default: Euro
            code:
              type: string
              default: EUR
    Resource:
      type: object
      required:
        - dsp_id
      properties:
        dsp_id:
          type: string
        title:
          type: string
        artists:
          type: string
          description: Multivalue, pipe-separated list of artist names.
        isrc:
          type: string
        usages:
          type: integer
        revenue:
          type: number
          format: double
        dsrs:
          type: array
          items:
            type: integer
          description: List of DSRs on which the resource is reported.
